from django.contrib import admin
from .models import Account, Contact, Action, MessageClick, \
    Message, List, Campaign, Send, Offset, Subscription, Statistics


class ClickInline(admin.TabularInline):
    model = MessageClick
    extra = 1


class MessageAdmin(admin.ModelAdmin):
    inlines = (ClickInline, )


admin.site.register(Account)
admin.site.register(Contact)
admin.site.register(Action)
admin.site.register(List)
admin.site.register(Campaign)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageClick)
admin.site.register(Send)
admin.site.register(Offset)
admin.site.register(Subscription)
admin.site.register(Statistics)