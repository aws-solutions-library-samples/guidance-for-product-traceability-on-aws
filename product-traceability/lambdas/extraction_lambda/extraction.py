import boto3
import os
import json
from datetime import datetime
import time

def lambda_handler(event, context):
    payload = event['Payload']

    textract = boto3.client('textract')
    detail = payload['detail']
    
    # Start the document analysis job
    response = textract.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': detail['bucket']['name'],
                'Name': detail['object']['key']
            }
        },
        FeatureTypes=['TABLES', 'QUERIES'],
        QueriesConfig={
            'Queries': [
                {
                    'Text': 'Until when is this document valid?',
                    'Alias': 'expiry_date',
                    'Pages': ['1']
                },
                {
                    'Text': 'Who is the certification body?',
                    'Alias': 'cert_body',
                    'Pages': ['1']
                },
                {
                    'Text': 'When was this document issued?',
                    'Alias': 'issue_date',
                    'Pages': ['1']
                },
                {
                    'Text': 'What is the certificate number?',
                    'Alias': 'cert_number',
                    'Pages': ['1']
                },
            ]
        }
    )
    
    # Get the job ID from the response
    job_id = response['JobId']
    
    # Wait for the job to complete using a waiter
    result = textract.get_document_analysis(JobId=job_id)
    while result['JobStatus'] not in ['SUCCEEDED', 'FAILED']:
        time.sleep(5)
        result = textract.get_document_analysis(JobId=job_id)
    
    output_dict = {}
    output_dict['queries'] = {}
    
    # Parse the query responses by matching queries with answers
    queries = []
    query_results = []
    for block in result['Blocks']:
        if block['BlockType'] == 'QUERY':
            queries.append(block)
        elif block['BlockType'] == 'QUERY_RESULT':
            query_results.append(block)
    for q in queries:
        for qr in query_results:
            if q['Relationships'][0]['Ids'][0] == qr['Id']:
                output_dict['queries'][q['Query']['Alias']] = {}
                output_dict['queries'][q['Query']['Alias']]['question'] = q['Query']['Text']
                output_dict['queries'][q['Query']['Alias']]['answer'] = qr['Text']
                output_dict['queries'][q['Query']['Alias']]['confidence'] = qr['Confidence']
                
    
    # Upload results
    s3 = boto3.resource('s3')
    s3object = s3.Object(os.environ['DOCUMENT_BUCKET_NAME'], f'data/demo_output.json')
    s3object.put(
        Body=(bytes(json.dumps(output_dict, indent=4, sort_keys=True).encode('UTF-8')))
    )
    
    return payload