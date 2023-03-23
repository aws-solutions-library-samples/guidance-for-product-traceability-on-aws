#############
# This function houses validation logic. 
# Current validation implementation acts as a placeholder for custom logic.
# Expected return:
#   EventBridge event with added "valid" field holding a boolen. False will end step-function execution before extraction.
#############

def lambda_handler(event, context):
    # Insert validation logic here
    # insert validation result in event['valid'] as a boolean
    if event['detail']['object']['key'].split('.')[-1] == 'pdf':
        event['valid'] = True
        
    else:
        event['valid'] = False
    
    return event