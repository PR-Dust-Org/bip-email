# Module handling the connection with the gmail API
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import os.path
import base64
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def credentials(creds_dir='secrets'):
    """Get credentials for the Gmail API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds_file = os.path.join(creds_dir, 'credentials.json')
    token_file = os.path.join(creds_dir, 'token.json')
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return creds


def gmail_api_client(creds_dir='secrets'):
    """Get the gmail API client."""
    return build('gmail', 'v1', credentials=credentials(creds_dir))


def get_header_value(headers, name):
    """Get the value of a header from the list of headers."""
    for header in headers:
        if header['name'] == name:
            return header['value']
    return None


def get_message_text_from_payload(message_part):
    """Get the message text from the message payload."""
    body = message_part['body']
    result = u''
    if 'data' in body:
        result += base64.urlsafe_b64decode(body['data']).decode('utf-8')
    parts = message_part.get('parts', [])
    for part in parts:
        if part['mimeType'] in ['text/plain']:
            result += get_message_text_from_payload(part)
    return result


def _display_thread(thread):
    """Display the thread's subject, and for each message,
    display the sender and body."""
    subject = get_header_value(thread['messages'][0]['payload']['headers'],
                               'Subject')
    print(f"====\nSubject: {subject}")
    for message in thread['messages']:
        sender = get_header_value(message['payload']['headers'], 'From')
        body = get_message_text_from_payload(message['payload'])
        print('\nSender: %s\nBody: %s' % (sender, body))


def get_last_threads(gmail_api_client, number_of_threads):
    """Get the last threads from Gmail.

    Doc: https://developers.google.com/gmail/api/v1/reference/users/threads/
    """
    try:
        response = gmail_api_client.users().threads().list(userId='me', maxResults=number_of_threads).execute()
        threads = response['threads']
        result = []
        for thread in threads:
            thread_id = thread['id']
            thread = gmail_api_client.users().threads().get(userId='me', id=thread_id).execute()
            result.append(thread)
        return result
    except HttpError as error:
        print('An error occurred: %s' % error)


def _get_message(gmail_client, message_head):
    """Get message from a message head returned by the gmail 'list' API call"""
    return (gmail_client.users().messages()
            .get(userId='me', id=message_head['id'])
            .execute())


def get_last_emails(gmail_client, last_update_date):
    """Get the last emails from Gmail

    Doc: https://developers.google.com/gmail/api/v1/reference/users/messages/
    :param gmail_client: the gmail API client
    :param last_update_date: the last update date
    """
    try:
        last_ts = last_update_date.timestamp()
        response = (gmail_client.users().messages()
                    .list(userId='me', q=f"after:2023-03-29")
                    .execute())
        message_heads = response['messages']
        if not message_heads:
            return []
        return list(map(lambda x: _get_message(gmail_client, x), message_heads))
    except HttpError as error:
        print('An error occurred: %s' % error)


def test_gmail_api():
    gmail_api_client = build('gmail', 'v1', credentials=credentials())
    # retrieve the last 3 threads from Gmail
    last_threads = get_last_threads(gmail_api_client, 3)

    # display the last 3 threads
    for thread in last_threads:
        _display_thread(thread)


if __name__ == '__main__':
    print('Test')
    # list messages' subjects from messages after march 29, 2023 at 9
    retrieval_date = datetime.datetime(2023, 3, 28, 9, 0, 0)
    messages = get_last_emails(gmail_api_client('../../secrets'), retrieval_date)
    for message in messages:
        print(message['snippet'])

