# TODO: Implement basic extraction

def lambda_handler(event, context):
    event = event['Payload']
    event['extraction_success'] = True

    return event