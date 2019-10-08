from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import (
    CrowdfundingFormCMSPlugin, CrowdfundingProgressCMSPlugin,
    CrowdfundingContributorsCMSPlugin
)
from .forms import DonationContributionForm


@plugin_pool.register_plugin
class CrowdfundingFormPlugin(CMSPluginBase):
    module = _("Crowdfunding")
    name = _('Crowdfunding Embed Form')
    render_template = "froide_crowdfunding/cms/plugins/form.html"
    model = CrowdfundingFormCMSPlugin
    text_enabled = True
    cache = False
    raw_id_fields = ('crowdfunding',)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['object'] = instance
        context['crowdfunding'] = instance.crowdfunding
        context['crowdfunding_contribute_urlname'] = (
            'crowdfunding:crowdfunding-start_contribution_donation'
        )
        context['crowdfunding_contribute_form'] = DonationContributionForm(
            user=context['request'].user
        )
        return context


@plugin_pool.register_plugin
class CrowdfundingProgressPlugin(CMSPluginBase):
    module = _("Crowdfunding")
    name = _('Crowdfunding Progress')
    render_template = "froide_crowdfunding/cms/plugins/progress.html"
    model = CrowdfundingProgressCMSPlugin
    text_enabled = True
    cache = True
    raw_id_fields = ('crowdfunding',)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['crowdfunding'] = instance.crowdfunding
        return context


@plugin_pool.register_plugin
class CrowdfundingContributorsPlugin(CMSPluginBase):
    module = _("Crowdfunding")
    name = _('Crowdfunding Contributors')
    render_template = "froide_crowdfunding/cms/plugins/contributors.html"
    model = CrowdfundingContributorsCMSPlugin
    text_enabled = True
    cache = True
    raw_id_fields = ('crowdfunding',)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['crowdfunding'] = instance.crowdfunding
        contributors = context['crowdfunding'].contribution_set.all()
        context['contributor_count'] = contributors.count()
        public_contributors = contributors.filter(
            public=True
        ).select_related('order')
        context['contributor_names'] = [
            c.order.get_full_name() for c in public_contributors[:20]
        ]
        context['contributor_count'] -= len(context['contributor_names'])
        return context
