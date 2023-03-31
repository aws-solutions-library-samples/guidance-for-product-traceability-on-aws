import boto3
import os
import textractcaller as tc
import trp.trp2 as t2
import json

def lambda_handler(event, context):
    payload = event['Payload']

    textract = boto3.client('textract')
    detail = payload['detail']
    
    # Define queries
    queries = [
        tc.Query(text='What is the certificate number at the bottom of the page?', alias='CERT_NO', pages=['1']),
        tc.Query(text='Until when is this document valid?', alias='EXPIRATION', pages=['1']),
        tc.Query(text='When was this document issued?', alias='ISSUE_DATE', pages=['1']),
    ]
    
    textract_response = tc.call_textract(
        input_document=f's3://{detail["bucket"]["name"]}/{detail["object"]["key"]}',
        queries_config=tc.QueriesConfig(queries=queries),
        features=[tc.Textract_Features.QUERIES],
        force_async_api=True,
        boto3_textract_client=textract
    )
    
    t_doc = t2.TDocumentSchema().load(textract_response)
    
    output_data = {}
    
    for page in t_doc.pages:
        query_answers = t_doc.get_query_answers(page=page)
        for x in query_answers:
            output_data[x[1]] = x[2]
    
    # Upload results
    s3 = boto3.resource('s3')
    s3object = s3.Object(os.environ['DOCUMENT_BUCKET_NAME'], 'output.json')
    s3object.put(
        Body=(bytes(json.dumps(output_data).encode('UTF-8')))
    )
    
    return payload