import aws_cdk as core
import aws_cdk.assertions as assertions

from product_traceability.product_traceability_stack import ProductTraceabilityStack

# example tests. To run these tests, uncomment this file along with the example
# resource in product_traceability/product_traceability_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ProductTraceabilityStack(app, "product-traceability")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
