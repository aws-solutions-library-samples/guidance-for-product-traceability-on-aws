import boto3
import time

def lambda_handler(event, context):
    payload = event['Payload']

    # Use textract boto3 client for information extraction
    textract = boto3.client('textract')
    detail = payload['detail']

    start_response = textract.start_document_analysis(
        DocumentLocation={
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
                    'Text': 'Until when is this document valid?',
                    'Alias': 'expiration',
                    'Pages': [
                        '1',
                    ]
                },
            ]
        }
    )

    print(f'Job submitted. ID: {start_response["JobId"]}. Waiting for job to finish.')
    
    # Wait for job to finish
    get_response = textract.get_document_analysis(
        JobId=start_response['JobId'],
    )
    wait_time = 0
    while get_response['JobStatus'] == 'IN_PROGRESS':
        sleep_time += 1
        print(f'Job not done. Sleeping for {sleep_time}s.')
        time.sleep(sleep_time)
        get_response = textract.get_document_analysis(
            JobId=start_response['JobId'],
        )

    # Log textract results
    print(get_response)

    return payload