import time
import json
import os
import urllib3

from bip.api import BipAPI

bip_api = BipAPI.api.BipAPI()


def respond200(infoMessage = "Request Handled"):
    return {
        "statusCode": 200,
        "body": json.dumps({"info": infoMessage})
    }


def send_message_unhandled(userId, message):
    """Send a message to the user via whatsapp, using the Whatsapp
    Business Platform Cloud API
    @param {string} message - The message to
    send to the user
    """
    url = "https://graph.facebook.com/v16.0/116575418039568/messages"
    token = os.getenv("META_WHATSAPP_TOKEN")
    body = {
        "messaging_product": "whatsapp",
        "to": userId,
        "text": {"body": message}}
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token}
    http = urllib3.PoolManager()
    r = http.request(
        "POST",
        url,
        body=json.dumps(body).encode('utf-8'),
        headers=headers)


def send_message(userId,message):
    sendResponse = send_message_unhandled(userId, message)
    if sendResponse.status == 200:
        return respond200("Request handled successfully")
    else:
        print("Error sending message")
        print(sendResponse)
        raise Exception("Error sending message to user")


def is_meta_graphapi_verification_request(event):
    """ Check if the request is a verification request
    :param event: The request event
    :return: True if the request is a verification request
    """
    return ('queryStringParameters' in event
            and event['queryStringParameters']['hub.mode'] == 'subscribe')


def handle_verification_request(event):
    """
    Handle the verification request
    :param event: The request event
    """
    if (event['queryStringParameters']['hub.verify_token'] 
        != 'BIP_VERIFICATION_TOKEN'):
        return {
            'statusCode': 401,
            'body': 'Unauthorized'
        }
    return f"{event['queryStringParameters']['hub.challenge']}"


def parse_message_from_event(event):
    """Parse the message from the request event sent by the Graph API
    :param event: The request event as a JSON object
    :return: The message object, with a field "text" containing the message 
    and a field "from" containing either "bip" or the user id
    """
    # catch error if one of the key is undefined
    try:
        body = json.loads(event['body'])
        data = body['entry'][0]['changes'][0]['value']['messages'][0]
        return {'from': data['from'],
                'text': data['text']['body'],
                'timestamp': data['timestamp']}
    except Exception as e:
        print("Parsing message failed")
        print(e)
        return None


def message_too_old(message):
    """Check if the hook notification is stale, that is, the user's message is more than 10 minutes old relatively to the current time
    """
    return (time.time() - float(message["timestamp"])) > 600


def user_message_notification(event):
    """Check if the request is a user message notification
    :param event: The request event
    :return: True if the request is a user message notification
    """
    body = json.loads(event["body"])    
    return body["entry"][0]["changes"][0]["value"]["messages"]


def handleRequest(event):
    if is_meta_graphapi_verification_request(event):
        return handle_verification_request(event)
    if not user_message_notification(event):
        return respond200("No need to handle, not a user message notification")
    message = parse_message_from_event(event)
    if not message:
        return respond200("Error parsing message")
    # Checking message is too old to avoid sending delayed responses to the
    # user. Notably, sometimes the Cloud API Webhooks retry sending
    # notifications when they did not receive a 200 response from the
    # webhook endpoint (this endpoint).
    if message_too_old(message):
        return respond200("Event too old, notification not handled")
    answer = {}
    try:
        if message["text"] == "ping":
            answer = {"from": "bip", "text": "pong"}
        else:
            print("Processing user message: " + message["text"])
            send_message(message["from"], "Ok, je cherche...")
            query_answer = bip_api.query_emails(message["text"])
            answer = {"from": "bip", 
                      "text":  "ready for bip Api for " + message['text']} # BipApi().query(message["text"])}
            print(answer)
    except Exception as e:
        print("Error processing user message")
        print(e)
        answer = {"from": "bip", 
                  "text": "Je buggue. Toutes mes excuses."}
    return send_message(message["from"], answer["text"])
    