from django.apps import AppConfig
from django.urls import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _


class FroideCrowdfundingConfig(AppConfig):
    name = 'froide_crowdfunding'
    verbose_name = _("Froide Crowdfunding App")

    def ready(self):
        # TODO: add export, cancel and merging user hooks
        from payments.signals import status_changed
        from froide.account.menu import menu_registry, MenuItem

        from . import contribution_successful
        from .listeners import (
            payment_status_changed, send_contribution_notification
        )

        status_changed.connect(payment_status_changed)
        contribution_successful.connect(send_contribution_notification)

        @menu_registry.register
        def get_campaign_menu_item(request):
            if not request.user.has_perm('froide_crowdfunding.can_crowdfund'):
                return None
            try:
                return MenuItem(
                    section='before_settings', order=10,
                    url=reverse('crowdfunding:crowdfunding-edit'),
                    label=_('Your crowdfundings')
                )
            except NoReverseMatch:
                return None
