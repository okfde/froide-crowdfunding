from django.apps import AppConfig
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class FroideCrowdfundingConfig(AppConfig):
    name = 'froide_crowdfunding'
    verbose_name = _("Froide Crowdfunding App")

    def ready(self):
        # FIXME: add export, cancel and merging user hooks
        from payments.signals import status_changed
        from froide.account.menu import menu_registry, MenuItem

        from .listeners import payment_status_changed

        status_changed.connect(payment_status_changed)

        @menu_registry.register
        def get_campaign_menu_item(request):
            if not request.user.is_staff:
                return None
            return MenuItem(
                section='before_settings', order=10,
                url=reverse('crowdfunding-edit'),
                label=_('Your crowdfundings')
            )
