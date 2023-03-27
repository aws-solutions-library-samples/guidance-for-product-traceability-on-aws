import boto3
import time
import pandas as pd
import os

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
                    'Text': 'What is the certificate number at the bottom of the page?',
                    'Alias': 'cert_no',
                    'Pages': [
                        '1',
                    ]
                },
                {
                    'Text': 'Until when is this document valid?',
                    'Alias': 'expiration',
                    'Pages': [
                        '1',
                    ]
                },
                {
                    'Text': 'When was this document issued?',
                    'Alias': 'issue_date',
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
    sleep_time = 0
    while get_response['JobStatus'] == 'IN_PROGRESS':
        sleep_time += 1
        print(f'Job not done. Sleeping for {sleep_time}s.')
        time.sleep(sleep_time)
        get_response = textract.get_document_analysis(
            JobId=start_response['JobId'],
        )

    # Parse results
    query_blocks = [[block['Query']['Text'], block['Query']['Alias'], block['Relationships'][0]['Ids'][0]] for block in get_response['Blocks'] if block['BlockType'] == 'QUERY']
    result_blocks = [[block['Id'], block['Text'], block['Confidence']] for block in get_response['Blocks'] if block['BlockType'] == 'QUERY_RESULT']

    # Create output dataframe
    query_df = pd.DataFrame(query_blocks, columns=['query_text', 'alias', 'merge_id'])
    result_df = pd.DataFrame(result_blocks, columns=['merge_id', 'answer', 'confidence'])
    final_df = pd.merge(query_df, result_df, on='merge_id', how='outer')
    final_df.to_csv(f'/tmp/output.csv', index=False, header=True)

    # Get id information for writing
    cert_no = final_df[final_df['alias'] == 'cert_no'].iloc[0]['answer']

    # Write to S3
    s3 = boto3.client('s3')
    s3.upload_file(
        '/tmp/output.csv',
        os.environ['DOCUMENT_BUCKET_NAME'],
        f'data/{cert_no}.csv'
    )

    return payload