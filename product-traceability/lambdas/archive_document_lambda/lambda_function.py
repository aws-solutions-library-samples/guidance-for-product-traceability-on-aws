import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    payload = event['Payload']
    bucket = payload['detail']['bucket']['name']
    source_key = payload['detail']['object']['key']
    filename = source_key.split('/')[-1]

    # Copy document to archive
    response = s3.copy_object(
        Bucket = bucket,
        CopySource = source_key,
        Key = '/archive/'+filename,
    )

    return response