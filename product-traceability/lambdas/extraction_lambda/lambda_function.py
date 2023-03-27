import boto3
import time

def lambda_handler(event, context):
    payload = event['Payload']

    # Use textract boto3 client for information extraction
    textract = boto3.client('textract')
    detail = payload['detail']

    start_response = textract.start_document_analysis(
        Document={
            'S3Object': {
                'Bucket': detail['bucket']['name'],
                'Name': detail['object']['key']
            }
        },
        FeatureTypes=[
            'QUERIES',
        ],
        QueriesConfig={
            'Queries': [
                {
                    'Text': 'When does this document expire?',
                    'Alias': 'expiration',
                    'Pages': [
                        '1',
                    ]
                },
            ]
        }
    )
    
    # Wait for job to finish
    get_response = textract.get_document_analysis(
        JobId=start_response['JobId'],
    )
    wait_time = 0
    while get_response['JobStatus'] == 'IN_PROGRESS':
        wait_time += 1
        time.sleep(wait_time)
        get_response = textract.get_document_analysis(
            JobId=start_response['JobId'],
        )

    return get_response