from django.contrib import admin
from subscriptions import models

#class KeywordInline(admin.StackedInline):
#    model = KeywordSubscription
#    extra = 3

#class CouncilmemberInline(admin.StackedInline):
#    model = CouncilMemberSubscription
#    extra = 3

#class SubscriptionAdmin(admin.ModelAdmin):
#    inlines = [KeywordInline, CouncilmemberInline]

#class LegActionInline(admin.StackedInline):
#    model = LegAction
#    extra = 1

class SubscriptionDispatchRecordInline(admin.TabularInline):
    model = models.SubscriptionDispatchRecord
    extra = 0

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionDispatchRecordInline]


admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.Subscriber)
admin.site.register(models.FeedRecord)

#admin.site.register(models.SearchSubscription)
#admin.site.register(models.EmailChannel)
#admin.site.register(models.RssChannel)
#admin.site.register(models.SmsChannel)
