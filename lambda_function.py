import bip.lambda_agent

"""
This is the entry point of the Lambda function. It just logs the
event/response and calls the handleRequest function
"""
def handler(event, context):
    print(event)
    response = bip.lambda_agent.handleRequest(event)
    print(response)
    return response
