# from aws_cdk import (
#     Stack,
#     Stage,
#     aws_codepipeline as codepipeline,
#     aws_codepipeline_actions as cpactions,
#     aws_secretsmanager as secretsmanager,
#     aws_iam as iam,
#     pipelines,
#     Environment,
# )
# from constructs import Construct
# from .app_stack import AppStack


# class AppStage(Stage):
#     def __init__(self, scope: Construct, id: str, *, env: Environment, **kwargs):
#         super().__init__(scope, id, env=env, **kwargs)
#         AppStack(self, "AppStack")


# class MultiBranchPipelineStack(Stack):
#     """
#     Deploy this stack into the pipeline account (Dev account).
#     It creates three independent pipelines:
#       - dev-pipeline (triggered by pushes to branch 'dev') -> deploys to DEV account
#       - stage-pipeline (triggered by pushes to branch 'stage') -> deploys to STAGE account (manual approval)
#       - prod-pipeline (triggered by pushes to branch 'prod') -> deploys to PROD account (manual approval)
#     """
#     def __init__(self, scope: Construct, id: str, *, github_owner: str, github_repo: str, secret_name: str, dev_env: Environment,
#         stage_env: Environment, prod_env: Environment, stage_approval_emails: list[str], prod_approval_emails: list[str], **kwargs ):
#         super().__init__(scope, id, **kwargs)

#         # Read CodeStar connection ARN from Secrets Manager
#         secret = secretsmanager.Secret.from_secret_name_v2(self, "ConnectionSecret", secret_name)
#         # connection_arn = secret.secret_value.to_string()

#         # Define a pipeline for each branch: dev, stage, prod
#         self.pipelines = {}
#         for branch_name, env, approval_emails in [
#             ("dev", dev_env, []),  # dev: no manual approval
#             ("stage", stage_env, stage_approval_emails),  # stage: manual approval
#             ("prod", prod_env, prod_approval_emails),  # prod: manual approval
#         ]:
#             pipeline = pipelines.CodePipeline(
#                 self, f"{branch_name.capitalize()}Pipeline",
#                 pipeline_name=f"{branch_name}-pipeline",
#                 synth=pipelines.ShellStep(
#                     "Synth",
#                     input=pipelines.CodePipelineSource.connection(
#                         repo_string = "kafui001/aws-codepipeline-test",
#                         branch = "main",
#                         connection_arn="arn:aws:codeconnections:us-west-2:648867426675:connection/138da170-e725-4eeb-9239-3cdce2d3a012",
#                     ),
#                     commands=[
#                         "pip install -r requirements.txt",
#                         "npm install -g aws-cdk@2",
#                         "cdk synth",
#                     ],
#                 ),
#                 cross_account_keys=True,
#             )

#             pre_steps = []
#             if approval_emails:
#                 pre_steps.append(
#                     pipelines.ManualApprovalStep(
#                         "ManualApproval",
#                         comment=f"Approve deployment to {branch_name.upper()}",
#                     )
#                 )

#             pipeline.add_stage(
#                 AppStage(self, f"{branch_name.capitalize()}Stage", env=env),
#                 pre=pre_steps,
#             )

#             self.pipelines[branch_name] = pipeline


###############
################

from aws_cdk import (
    Stack,
    Stage,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms as kms,
    pipelines,
    Environment,
    RemovalPolicy,
)
from constructs import Construct
from .app_stack import AppStack


class AppStage(Stage):
    def __init__(self, scope: Construct, id: str, *, env: Environment, **kwargs):
        super().__init__(scope, id, env=env, **kwargs)
        AppStack(self, "AppStack")


class MultiBranchPipelineStack(Stack):
    """
    Deploy this stack into the pipeline account (Dev account).
    Creates three independent pipelines sharing the same artifact bucket/KMS key:
      - dev-pipeline (branch 'dev') -> DEV account
      - stage-pipeline (branch 'stage') -> STAGE account (manual approval)
      - prod-pipeline (branch 'prod') -> PROD account (manual approval)
    """
    def __init__(self, scope: Construct, id: str, *,
                 github_owner: str,
                 github_repo: str,
                 secret_name: str,
                 dev_env: Environment,
                 stage_env: Environment,
                #  prod_env: Environment,
                 stage_approval_emails: list[str],
                #  prod_approval_emails: list[str],
                 **kwargs):
        super().__init__(scope, id, **kwargs)

        # Shared KMS key
        artifact_key = kms.Key(
            self, "ArtifactKey",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Grant cross-account usage for Stage & Prod
        for account in [stage_env.account 
                        # prod_env.account
                        ]:
            artifact_key.add_to_resource_policy(
                iam.PolicyStatement(
                    actions=[
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:DescribeKey"
                    ],
                    principals=[iam.AccountPrincipal(account)],
                    resources=["*"]
                )
            )

        # Shared artifact bucket
        artifact_bucket = s3.Bucket(
            self, "ArtifactBucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=artifact_key,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Grant cross-account bucket access for Stage & Prod
        for account in [stage_env.account
                        # prod_env.account
                        ]:
            artifact_bucket.add_to_resource_policy(
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject",
                        "s3:GetObjectVersion",
                        "s3:PutObject"
                    ],
                    principals=[iam.AccountPrincipal(account)],
                    resources=[artifact_bucket.arn_for_objects("*")]
                )
            )
            artifact_bucket.add_to_resource_policy(
                iam.PolicyStatement(
                    actions=["s3:ListBucket"],
                    principals=[iam.AccountPrincipal(account)],
                    resources=[artifact_bucket.bucket_arn]
                )
            )

        # Read CodeStar connection ARN
        # secret = secretsmanager.Secret.from_secret_name_v2(self, "ConnectionSecret", secret_name)

        # Pipelines for each branch
        self.pipelines = {}
        for branch_name, env, approval_emails in [
            ("dev", dev_env, []),
            ("stage", stage_env, stage_approval_emails),
            # ("prod", prod_env, prod_approval_emails),
        ]:
            pipeline = pipelines.CodePipeline(
                self, f"{branch_name.capitalize()}Pipeline",
                pipeline_name=f"{branch_name}-pipeline",
                artifact_bucket=artifact_bucket,
                cross_account_keys=True,  # still true, but using shared key/bucket
                synth=pipelines.ShellStep(
                    "Synth",
                    self_mutation=True,
                    input=pipelines.CodePipelineSource.connection(
                        repo_string=f"{github_owner}/{github_repo}",
                        branch=branch_name,
                        # connection_arn=secret.secret_value.to_string(),
                        connection_arn="arn:aws:codeconnections:us-west-2:648867426675:connection/138da170-e725-4eeb-9239-3cdce2d3a012",
                    ),
                    commands=[
                        "pip install -r requirements.txt",
                        "npm install -g aws-cdk@2",
                        "cdk synth",
                    ],
                ),
            )

            pre_steps = []
            if approval_emails:
                pre_steps.append(
                    pipelines.ManualApprovalStep(
                        "ManualApproval",
                        comment=f"Approve deployment to {branch_name.upper()}",
                    )
                )

            pipeline.add_stage(
                AppStage(self, f"{branch_name.capitalize()}Stage", env=env),
                pre=pre_steps,
            )

            self.pipelines[branch_name] = pipeline


