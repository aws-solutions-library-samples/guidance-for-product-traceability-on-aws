from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam
)
from constructs import Construct

class ProductTraceabilityStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Bucket for documents. 
        # Includes lifecycle rules for long term archival - safe to remove "transitions" parameter
        # Note: EventBridge enabled required
        document_bucket = s3.Bucket(self, "DocumentBucket",
            lifecycle_rules = [
                s3.LifecycleRule(
                    id = "EventuallyDeepArchival",
                    prefix = "archive",
                    transitions = [
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER_INSTANT_RETRIEVAL,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(120)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.DEEP_ARCHIVE,
                            transition_after=Duration.days(360)
                        )
                    ]
                )
            ],
            event_bridge_enabled = True
        )

        # Lambda function for file validation before extraction
        validation_lambda_function = aws_lambda.Function(self, "ValidationFunction",
            runtime = aws_lambda.Runtime.PYTHON_3_9,
            handler = 'lambda_function.lambda_handler',
            code = aws_lambda.Code.from_asset('lambdas/validation_lambda')
        )

        # Lambda function for handling Textract calls and extraction logic.
        extraction_lambda_function = aws_lambda.Function(self, "ExtractionFunction",
            runtime = aws_lambda.Runtime.PYTHON_3_9,
            handler = 'lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('lambdas/extraction_lambda')
        )

        # Lambda function for archiving file.
        archive_lambda_function = aws_lambda.Function(self, "DocumentArchivalFunction",
            runtime = aws_lambda.Runtime.PYTHON_3_9,
            handler = 'lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('lambdas/archive_document_lambda')
        )
        archive_lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:DeleteObject"],
                resources=[f'{document_bucket.bucket_arn}/landing/*']
            )
        )
        archive_lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[f'{document_bucket.bucket_arn}/archive/*']
            )
        )

        ## Step function state definitions ##

        # Call the document validation lambda
        validate_document = tasks.LambdaInvoke(self, "ValidateDocument", lambda_function = validation_lambda_function)
        # Validation fail state
        validation_fail = sfn.Fail(self, "Invalid", cause = "Document is not valid.", error="validate_document returned False")
        validate_document.add_catch(validation_fail)
        # Call the document extraction lambda
        extract_information = tasks.LambdaInvoke(self, "ExtractData", lambda_function = extraction_lambda_function)
        # Extraction fail state
        extraction_fail = sfn.Fail(self, "ExtractionFail", cause = "Exctraction was unsuccessful.", error="extract_information failed")
        extract_information.add_catch(extraction_fail)
        # Call the document archival lambda
        archive_document = tasks.LambdaInvoke(self, "ArchiveDocument", lambda_function = archive_lambda_function)
        # Archival fail state
        archival_fail = sfn.Fail(self, "ArchivalFail", cause = "Check lambda permissions.", error="Object could not be moved to archive.")
        archive_document.add_catch(archival_fail)
        # Success state
        success_state = sfn.Succeed(self, "Success")
        
        # Create flow definition
        flow_definition = validate_document.next(
            extract_information).next(
            archive_document).next(
            success_state)

        # Create state machine
        extraction_state_machine = sfn.StateMachine(self, "ExtractionStateMachine",
            definition = flow_definition
        )

        # Create eventbridge rule for uploads with "landing/" prefix
        landing_upload_rule = events.Rule(self, "NewDocumentRule",
            description = 'S3 Rule to trigger extraction step function when files with "landing" prefix are created.',
            event_pattern = events.EventPattern(
                source = ["aws.s3"],
                resources = [document_bucket.bucket_arn],
                detail_type = ["Object Created"],
                detail = {
                    "object": {
                        "key": [{"prefix": "landing/"}]
                    }
                }
            )
        )
        
        # Add state machine as rule target
        landing_upload_rule.add_target(
            targets.SfnStateMachine(extraction_state_machine) 
        )