from .icontact_api import IContactSession
from .models import Account, Message, Send
from django.contrib import messages


def establish_iContact_session(account_name):
        account = Account.objects.get(name=account_name)
        #TODO: handle invalid name nicely.

        url = account.base_url
        username = account.username
        password = account.password
        appId = account.app_id

        # Obtaining your iContact accountId and folderId
        ic = IContactSession.connect(url, appId, username, password)

        return ic


def upload_message(issue, request=None):
    account_name = issue.newsletter.sender_account.name
    session = establish_iContact_session(account_name)

    if issue.message:
        message_data = {
            'messageId': issue.message.message_id,
            'campaignId': issue.newsletter.campaign.campaign_id,
            'subject': issue.subject,
            'htmlBody': issue.html,
            'textBody': issue.text,
        }

        response = session.messages.add_or_update([message_data])
    else:

        message_data = {
            'campaignId': issue.newsletter.campaign.campaign_id,
            'messageType': 'normal',
            'subject': issue.subject,
            'htmlBody': issue.html,
            'textBody': issue.text,
            'messageName': issue.name
        }

        response = session.message.add(message_data)

    json_content = response.json_content

    for warning in json_content.get('warnings', []):
        if request:
            messages.warning(request, warning)

    for error in json_content.get('errors', []):
        if request:
            messages.warning(request, error)

    messages_data = json_content.get('messages', [])
    if messages_data:
        message_data = messages_data[0]
        message, created = Message.objects.get_or_create(
            message_id=message_data['messageId'])
        message.campaign = issue.newsletter.campaign
        message.message_name = message_data['messageName']
        message.message_type = message_data['messageType']
        message.subject = message_data['subject']
        message.html_body = message_data['htmlBody']
        message.text_body = message_data['textBody']
        message.create_date = message_data['createDate']
        message.save()

        issue.message = message
        issue.save()


#TODO: how to resend a message
#{u'sends': [], u'warnings': [u'Message [messageId=252088] already scheduled for send [sendId=978889]']}
def send_message(issue, test_message=True, request=None):
    account_name = issue.newsletter.sender_account.name
    session = establish_iContact_session(account_name)

    send_to_list = None
    if test_message:
        send_to_list = issue.newsletter.testing_list
    else:
        send_to_list = issue.newsletter.associated_list

    message = issue.message

    if send_to_list and message:
        send_data = {
            'messageId': message.message_id,
            'includeListIds': send_to_list.list_id
        }

        response = session.sends.add_or_update([send_data])

        json_content = response.json_content

        for warning in json_content.get('warnings', []):
            if request:
                messages.warning(request, warning)

        for error in json_content.get('errors', []):
            if request:
                messages.warning(request, error)

        for send_data in json_content['sends']:
            send = Send.objects.create(
                send_id=send_data['sendId'],
                message=message,
                list=send_to_list,
                recipient_count=int(send_data['recipientCount']),
                status=send_data['status'],
                released_time=send_data['releasedTime']
            )

