from django.core.management.base import BaseCommand
from optparse import make_option
from icontact.models import Contact, Action, Message, \
    MessageClick, List, Campaign, Offset, Subscription, SpamCheck, \
    SpamCheckDetail, Statistics
from django.utils import timezone
from icontact.utils import establish_iContact_session


class Command(BaseCommand):
    args = '<account_name>'
    option_list = BaseCommand.option_list + (
        make_option('--data-type', '-d', dest='data_type',
                    help="The type of data to import"),
        make_option('--related-limit', '-l', dest='related_limit',
                    help='Limit for importing items'),
    )
    help = 'Imports iContact data'

    def handle(self, *args, **options):
        account_name = args[0]
        data_type = options.get('data_type', "contacts")

        session = establish_iContact_session(account_name)

        if data_type == "contacts":
            offset, created = Offset.objects.get_or_create(data_type=data_type)
            self.import_contacts(session, offset)

        if data_type == "contact_history":
            related_limit = int(options.get('related_limit', 1000))
            contacts = Contact.objects.order_by(
                'history_last_updated')[:related_limit]

            for contact in contacts:
                self.import_history(contact, session)

        if data_type == "lists":
            self.import_lists(session)

        if data_type == "campaigns":
            self.import_campaigns(session)

        if data_type == "messages":
            offset, created = Offset.objects.get_or_create(data_type=data_type)
            self.import_messages(session, offset)

        if data_type == "clicks":
            related_limit = int(options.get('related_limit', 1000))
            messages = Message.objects.order_by(
                'clicks_last_updated')[:related_limit]

            for message in messages:
                self.import_clicks(message, session)

        if data_type == "subscriptions":
            lists = List.objects.all()
            for contact_list in lists:
                self.import_subscriptions(contact_list, session)

        if data_type == "statistics":
            related_limit = int(options.get('related_limit', 1000))
            messages = Message.objects.order_by(
                'statistics_last_updated')[:related_limit]

            for message in messages:
                self.import_statistics(message, session)

    def import_lists(self, session):

        response = session.lists.get(options={
            'limit': 25,
        })

        json_content = response.json_content

        for list_data in json_content['lists']:
            contact_list, created = List.objects.get_or_create(
                list_id=list_data['listId'])
            contact_list.name = list_data['name']
            contact_list.description = list_data['description']
            contact_list.email_owner_on_change = int(list_data['emailOwnerOnChange'])
            contact_list.welcome_on_manual_add = int(list_data['welcomeOnManualAdd'])
            contact_list.welcome_on_signup_add = int(list_data['welcomeOnSignupAdd'])
            welcome_message_id = list_data['welcomeMessageId']
            if welcome_message_id:
                contact_list.welcome_message_id = int(welcome_message_id)

            contact_list.save()



    def import_campaigns(self, session):
        response = session.campaigns.get(options={
            'limit': 1000,
        })

        json_content = response.json_content

        for campaign_data in json_content['campaigns']:
            campaign, created = Campaign.objects.get_or_create(
                campaign_id=campaign_data['campaignId'])
            campaign.name = campaign_data['name']
            campaign.from_name = campaign_data['fromName']
            campaign.from_email = campaign_data['fromEmail']
            campaign.forward_to_friend = campaign_data['forwardToFriend']
            campaign.subscription_management = campaign_data['subscriptionManagement']
            campaign.click_track_mode = campaign_data['clickTrackMode']
            campaign.use_account_address = campaign_data['useAccountAddress']
            campaign.archive_by_default = campaign_data['archiveByDefault']
            campaign.description = campaign_data['description']
            campaign.street = campaign_data['street']
            campaign.city = campaign_data['city']
            campaign.state = campaign_data['state']
            campaign.zip = campaign_data['zip']
            campaign.country = campaign_data['country']

            campaign.save()

    def import_messages(self, session, offset):
        limit = 50
        total = 0
        processed = 0
        offset_value = offset.offset

        while True:
            response = session.messages.get(options={
                'limit': limit,
                'offset': offset_value
            })

            json_content = response.json_content
            errors = json_content.get('errors', [])

            if not errors:
                total = json_content.get('total')

                count = 0
                for message_data in json_content['messages']:
                    count += 1
                    message, created = Message.objects.get_or_create(
                        message_id=message_data['messageId'])
                    campaign_id = message_data['campaignId']
                    if campaign_id:
                        campaign = Campaign.objects.get(campaign_id=campaign_id)
                        message.campaign = campaign
                    message.message_type = message_data['messageType']
                    message.subject = message_data['subject']
                    message.html_body = message_data['htmlBody']
                    message.text_body = message_data['textBody']
                    message.message_name = message_data['messageName']
                    message.create_date = message_data['createDate']

                    message.save()

                    if not message.spam_check:
                        message.spam_check = SpamCheck()

                    spam_check_data = message_data['spamCheck']
                    message.spam_check.raw_score = spam_check_data['rawScore']
                    message.spam_check.save()

                    message.spam_check.spam_check_detail_set.delete()

                    spam_check_details_data = spam_check_data['spamDetails']
                    for detail in spam_check_details_data:
                        spam_check_detail = SpamCheckDetail(spam_check=message.spam_check)
                        spam_check_detail.score = detail['spamDetailScore']
                        spam_check_detail.name = detail['spamDetailName']
                        spam_check_detail.description = detail['spamDetailDescription']
                        spam_check_detail.save()

                    message.save()

                offset_value += count
                processed += count
            else:
                print('encountered errors: %s. processed: %s, total: %s' % ('\n'.join(errors), processed, total))
                offset_value += limit

            if offset_value >= total:
                break

        if total > offset.offset:
            print('Expected %s messages, found %s, started at offset: %s' % (total, processed, offset.offset))

        offset.offset = offset_value
        offset.save()

    def import_clicks(self, message, session):
        response = session.clicks.get(message.message_id,
                                        {'limit': 10000, })

        json_content = response.json_content
        total = json_content['total']

        count = 0
        for click_data in json_content['clicks']:
            count += 1
            contact_id = click_data["contactId"]

            try:
                contact = Contact.objects.get(contact_id=contact_id)

                filter_arguments = dict(
                    contact=contact,
                    message=message,
                        click_time=click_data['clickTime'],
                        click_link=click_data['clickLink']
                )
            except Contact.DoesNotExist:
                filter_arguments = dict(
                    unmatched_contact_id=contact_id,
                        message=message,
                        click_time=click_data['clickTime'],
                        click_link=click_data['clickLink']
                )

            try:
                click, created = MessageClick.objects.get_or_create(
                    **filter_arguments
                )
            except MessageClick.MultipleObjectsReturned:
                clicks = MessageClick.objects.filter(
                    **filter_arguments
                )
                click = clicks[0]
                for extra_click in clicks[1:]:
                    extra_click.delete()

            click.save()

        message.clicks_last_updated = timezone.localtime(timezone.now())
        message.save()

        if count != total:
            print('Expected %s actions, found %s' % (total, count))

    def import_contacts(self, session, offset):
        limit = 2000
        total = 0
        processed = 0
        offset_value = offset.offset

        while True:
            response = session.contacts.get(options={
                'limit': limit,
                'offset': offset_value,
                # 'orderby': 'createDate',
                'status': 'total',
            })

            json_content = response.json_content
            errors = json_content.get('errors', [])

            if not errors:
                total = json_content.get('total')

                count = 0
                for contact_data in json_content['contacts']:
                    count += 1
                    contact, created = Contact.objects.get_or_create(
                        contact_id=contact_data['contactId'])
                    contact.first_name = contact_data['firstName']
                    contact.last_name = contact_data['lastName']
                    contact.email = contact_data['email']
                    contact.status = contact_data['status']
                    contact.save()

                offset_value += count
                processed += count
            else:
                print('Encountered errors processing contacts: %s. processed: %s, total: %s' %
                      ('\n'.join(errors), processed, total))
                offset_value += limit

            if offset_value >= total:
                break

        if total > offset.offset and (offset.offset + processed != total):
            print('Expected %s contacts, found %s, started at offset: %s' %
                  (total, processed, offset.offset))

        offset.offset = offset_value
        offset.save()

    def import_subscriptions(self, contact_list, session):
        response = session.subscriptions.get({'listId': contact_list.list_id,
                                              'limit': 20000, })

        json_content = response.json_content
        total = json_content['total']


        count = 0
        for subscription_data in json_content['subscriptions']:
            contact_id = subscription_data['contactId']
            status = subscription_data['status']
            #add_date = subscription_data['addDate']

            try:
                contact = Contact.objects.get(contact_id=contact_id)
                count += 1
                subscription, created = Subscription.objects.get_or_create(
                    list=contact_list,
                    contact=contact
                )
                subscription.status = status
                subscription.save()
            except Contact.DoesNotExist:
                print('Contact does not exist: {}'.format(contact_id))

        if count != total:
            print('Expected %s subscriptions, found %s' % (total, count))

    def import_history(self, contact, session):
        response = session.contact_history.get(contact.contact_id,
                                               {'limit': 10000, })

        json_content = response.json_content
        total = json_content['total']

        count = 0
        for action_data in json_content['actions']:
            count += 1
            try:
                action, created = Action.objects.get_or_create(
                    action_type=action_data['actionType'],
                    actor=action_data['actor'],
                    action_time=action_data['actionTime'],
                    contact=contact
                    )
            except Action.MultipleObjectsReturned:
                actions = Action.objects.filter(
                    action_type=action_data['actionType'],
                    actor=action_data['actor'],
                    action_time=action_data['actionTime'],
                    contact=contact
                )
                action = actions[0]
                for extra_action in actions[1:]:
                    extra_action.delete()

            action.details = action_data['details']
            action.save()

        contact.history_last_updated = timezone.localtime(timezone.now())
        contact.save()

        if count != total:
            print('Expected %s actions, found %s' % (total, count))

    def import_statistics(self, message, session):
        response = session.statistics.get(message.message_id,
                                          {'limit': 10000, })

        json_content = response.json_content

        count = 0
        statistics_data = json_content['statistics']

        statistics, created = Statistics.objects.get_or_create(message=message)
        statistics.bounces = statistics_data['bounces']
        statistics.delivered = statistics_data['delivered']
        statistics.unsubscribes = statistics_data['unsubscribes']
        statistics.unique_opens = statistics_data['opens']['unique']
        statistics.total_opens = statistics_data['opens']['total']
        statistics.unique_clicks = statistics_data['clicks']['unique']
        statistics.total_clicks = statistics_data['clicks']['total']
        statistics.forwards = statistics_data['forwards']
        statistics.comments = statistics_data['comments']
        statistics.complaints = statistics_data['complaints']

        statistics.save()

        message.statistics_last_updated = timezone.localtime(timezone.now())
        message.save()
