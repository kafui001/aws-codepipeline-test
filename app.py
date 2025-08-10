# #!/usr/bin/env python3
# import os

# import aws_cdk as cdk

# from aws_codepipeline_test.aws_codepipeline_test_stack import AwsCodepipelineTestStack


# app = cdk.App()
# AwsCodepipelineTestStack(app, "AwsCodepipelineTestStack",
#     # If you don't specify 'env', this stack will be environment-agnostic.
#     # Account/Region-dependent features and context lookups will not work,
#     # but a single synthesized template can be deployed anywhere.

#     # Uncomment the next line to specialize this stack for the AWS Account
#     # and Region that are implied by the current CLI configuration.

#     #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

#     # Uncomment the next line if you know exactly what Account and Region you
#     # want to deploy the stack to. */

#     #env=cdk.Environment(account='123456789012', region='us-east-1'),

#     # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
#     )

# app.synth()

##############
#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.pipeline_stack import MultiBranchPipelineStack

app = App()

# Account and region definitions for deployments
DEV_ENV = Environment(account="648867426675", region="us-west-2")
STAGE_ENV = Environment(account="265466609227", region="us-west-2")
# PROD_ENV = Environment(account="333333333333", region="us-west-2")

main_pipeline = MultiBranchPipelineStack(
    app,
    "PipelineStack",
    github_owner="kafui001",
    github_repo="aws-codepipeline-test",
    secret_name="github/connection-arn",
    dev_env=DEV_ENV,
    stage_env=STAGE_ENV,
    # prod_env=PROD_ENV,
    stage_approval_emails=["kafui01@yahoo.com"],
    # prod_approval_emails=["kafui01@yahoo.com"],
    env=DEV_ENV,  # Pipeline stack deployed in Dev account
)

app.synth()


