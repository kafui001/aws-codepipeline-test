from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class AppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self, "AppBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        table = dynamodb.Table(
            self, "AppTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        fn = _lambda.Function(
            self, "AppHandler",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="demo_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda"), 
            timeout=Duration.seconds(10),
            environment={
                "BUCKET": bucket.bucket_name,
                "TABLE": table.table_name
            }
        )

        bucket.grant_read_write(fn)
        table.grant_read_write_data(fn)
