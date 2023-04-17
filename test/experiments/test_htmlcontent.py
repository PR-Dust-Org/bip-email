# Get message with id 187424c7b4350332, get the html content,
# extract the text from the html content, and display the result

from bip.email import gmail, test_email


if __name__ == '__main__':
    gmail_api_client = gmail.gmail_api_client(test_email)
    message = (gmail_api_client.users().messages()
               .get(userId='me', id='187424c7b4350332')
               .execute())
    html_content = gmail.get_message_text_from_payload(message['payload'])
    print(html_content)
