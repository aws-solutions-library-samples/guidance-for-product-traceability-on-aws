# This function houses validation logic.

def lambda_handler(event, context):
    if event['detail']['object']['key'].split('.')[-1] == 'pdf':
        event['valid'] = True
        
    else:
        event['valid'] = False
    
    return event