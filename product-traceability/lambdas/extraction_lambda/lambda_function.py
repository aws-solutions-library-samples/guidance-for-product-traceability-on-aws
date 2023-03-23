# TODO: Implement basic extraction

def lambda_handler(event, context):
    payload = event['Payload']
    payload['extraction_success'] = True

    return payload