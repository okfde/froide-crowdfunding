__version__ = "0.0.1"

from django.dispatch import Signal

default_app_config = "froide_crowdfunding.apps.FroideCrowdfundingConfig"

contribution_successful = Signal()  # providing args ["contribution"]
