from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from froide.helper.email_sending import send_template_email
from froide.helper.admin_utils import ForeignKeyFilter

from .models import Crowdfunding, Contribution


class CrowdfundingAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ('request', 'user')
    list_display = (
        'title', 'status', 'kind', 'user', 'date_requested',
        'amount_needed', 'amount_raised'
    )
    list_filter = ('status', 'kind')

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            context = {
                'user': obj.user,
                'crowdfunding': obj,
                'site_name': settings.SITE_NAME,
                'url': obj.get_absolute_domain_url()
            }
            if obj.status == 'denied':
                send_template_email(
                    user=obj.user,
                    subject=_(
                        '💸 Your crowdfunding project needs review'
                    ),
                    template='froide_crowdfunding/emails/denied.txt',
                    context=context
                )
            elif obj.status == 'running':
                send_template_email(
                    user=obj.user,
                    subject=_(
                        '💸 Your crowdfunding project has been activated'
                    ),
                    template='froide_crowdfunding/emails/created.txt',
                    context=context
                )
        super().save_model(request, obj, form, change)


class ContributionAdmin(admin.ModelAdmin):
    raw_id_fields = ('crowdfunding', 'user', 'order')
    list_display = (
        'get_email', 'amount', 'timestamp',
        'crowdfunding',
        'status', 'public', 'user'
    )
    list_filter = (
        'status', 'public',
        ('crowdfunding', ForeignKeyFilter)
    )
    search_fields = ('crowdfunding__title',)
    date_hierarchy = 'timestamp'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            'crowdfunding', 'user', 'order'
        )
        return qs


admin.site.register(Crowdfunding, CrowdfundingAdmin)
admin.site.register(Contribution, ContributionAdmin)
