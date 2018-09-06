from django.contrib import admin

from .models import Crowdfunding, Contribution


class CrowdfundingAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ('request', 'user')
    list_display = (
        'title', 'status', 'kind', 'user', 'date_requested',
        'amount_needed', 'amount_raised'
    )
    list_filter = ('status', 'kind')


class ContributionAdmin(admin.ModelAdmin):
    raw_id_fields = ('crowdfunding', 'user', 'order')


admin.site.register(Crowdfunding, CrowdfundingAdmin)
admin.site.register(Contribution, ContributionAdmin)
