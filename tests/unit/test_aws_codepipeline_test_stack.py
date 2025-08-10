import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_codepipeline_test.aws_codepipeline_test_stack import AwsCodepipelineTestStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_codepipeline_test/aws_codepipeline_test_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCodepipelineTestStack(app, "aws-codepipeline-test")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
