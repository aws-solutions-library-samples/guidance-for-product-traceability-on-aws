# This function houses validation logic.

# In its current state, this function will only check whether a file is a pdf.

def lambda_handler(event, context):    
    assert event['detail']['object']['key'].split('.')[-1] == 'pdf'

    return event