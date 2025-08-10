from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    pipelines as pipelines,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codecommit as codecommit,
    aws_iam as iam,
    Environment as env
)
from constructs import Construct
from resource_stack.resource_stack import ResourceStack


class DeployStage(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, id, env=env, **kwargs)

        resource_stack = ResourceStack(self, "ResourceStack", env=env, stack_name="resource-stack-deploy")

class AwsCodepipelineTestStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        git_input = pipelines.CodePipelineSource.connection(
            repo_string = "kafui001/aws-codepipeline-test",
            branch = "main",
            connection_arn="arn:aws:codeconnections:us-west-2:648867426675:connection/138da170-e725-4eeb-9239-3cdce2d3a012",
        )

        code_pipeline = codepipeline.Pipeline(
            self, "CodePipeline", 
            pipeline_name="new-pipeline",
            cross_account_keys=False
        )

        synth_step = pipelines.ShellStep(
            "Synth",
            input=git_input,
            install_commands=[
                "npm install -g aws-cdk",
                "python -m pip install -r requirements.txt"
            ],
            commands=[
                "cdk synth"
            ],
            
        )

        
