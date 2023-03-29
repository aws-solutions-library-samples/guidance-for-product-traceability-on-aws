# This function houses validation logic.

def lambda_handler(event, context):    
    assert event['detail']['object']['key'].split('.')[-1] == 'pdf'

    return event