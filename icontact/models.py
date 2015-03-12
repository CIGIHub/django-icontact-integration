from django.db import models


class Account(models.Model):
    name = models.CharField(max_length=20)
    base_url = models.URLField()
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    app_id = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name


class List(models.Model):
    list_id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    public_name = models.CharField(max_length=255, null=True, blank=True)
    email_owner_on_change = models.IntegerField(default=1)
    welcome_on_manual_add = models.IntegerField(default=0)
    welcome_on_signup_add = models.IntegerField(default=0)
    welcome_message_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.name


class Campaign(models.Model):
    campaign_id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    from_email = models.EmailField()
    from_name = models.TextField()
    forward_to_friend = models.IntegerField(default=0)
    subscription_management = models.IntegerField(default=0)
    click_track_mode = models.IntegerField(default=1)
    use_account_address = models.IntegerField(default=0)
    archive_by_default = models.IntegerField(default=1)
    street = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.name


class Message(models.Model):
    message_id = models.IntegerField()
    message_name = models.CharField(max_length=1024, null=True, blank=True)
    campaign = models.ForeignKey("Campaign", null=True, blank=True)
    message_type = models.CharField(max_length=25, null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    html_body = models.TextField(null=True, blank=True)
    text_body = models.TextField(null=True, blank=True)
    create_date = models.CharField(max_length=30, null=True, blank=True)
    # raw_score = models.FloatField()
    # spam_detail_score = models.FloatField()
    # spam_detail_name = models.TextField()
    # spam_detail_description = models.TextField()
    clicks_last_updated = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        if self.message_name:
            return u'%s' % self.message_name
        else:
            return u'%s' % self.subject


class MessageClick(models.Model):
    message = models.ForeignKey("Message")
    contact = models.ForeignKey("Contact", null=True, blank=True)
    unmatched_contact_id = models.IntegerField(null=True, blank=True)
    click_time = models.CharField(max_length=30)
    click_link = models.TextField()


class Contact(models.Model):
    contact_id = models.CharField(max_length=50)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    status = models.CharField(max_length=30)
    history_last_updated = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)


class Action(models.Model):
    contact = models.ForeignKey("Contact")
    action_type = models.CharField(max_length=50, null=True, blank=True)
    action_time = models.CharField(max_length=50)
    actor = models.CharField(max_length=50)
    details = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"%s %s - %s - %s" % (self.contact.first_name,
                                     self.contact.last_name,
                                     self.action_type,
                                     self.action_time)


class Send(models.Model):
    send_id = models.IntegerField()
    message = models.ForeignKey('Message')
    list = models.ForeignKey('List')
    recipient_count = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=25, null=True, blank=True)
    released_time = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.send_id


class Offset(models.Model):
    data_type = models.CharField(max_length=25)
    offset = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s - %s" % (self.data_type, self.offset)


class Subscription(models.Model):
    contact = models.ForeignKey("Contact")
    list = models.ForeignKey("List")
    status = models.CharField(max_length=30) # normal, pending, unsubscribed
    last_updated = models.DateTimeField(auto_now=True)
