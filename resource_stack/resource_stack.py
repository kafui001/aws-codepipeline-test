from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_s3 as s3,
    RemovalPolicy
    
)
from constructs import Construct

class ResourceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # example resource
        queue = sqs.Queue(
            self, "AwsCodepipelineTestQueue",
            visibility_timeout=Duration.seconds(300),
            queue_name="demo_queue"
        )

        function = _lambda.Function(self, "AwsCodepipelineTestFunction",
                                    runtime=_lambda.Runtime.PYTHON_3_13,
                                    handler="demo_lambda.lambda_handler",
                                    code=_lambda.Code.from_asset("./lambda_code_demo"),
                                    function_name="codepipeline_lambda"
                                    )
        
        bucket = s3.Bucket(self, "MyfirstBucket",
                           bucket_name="demo-bucket-beyond-the-cloud-01234567890",
                           versioned=True,
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                           removal_policy=RemovalPolicy.DESTROY
                           )
