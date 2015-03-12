from django.contrib import admin
from .models import Account, Contact, Action, MessageClick, \
    Message, List, Campaign, Send, Offset, Subscription

admin.site.register(Account)
admin.site.register(Contact)
admin.site.register(Action)
admin.site.register(List)
admin.site.register(Campaign)
admin.site.register(Message)
admin.site.register(MessageClick)
admin.site.register(Send)
admin.site.register(Offset)
admin.site.register(Subscription)