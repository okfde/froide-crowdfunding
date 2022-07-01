from django.utils.translation import gettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class CrowdfundingCMSApp(CMSApp):
    name = _("Crowdfunding CMS App")
    app_name = "crowdfunding"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["froide_crowdfunding.urls"]
