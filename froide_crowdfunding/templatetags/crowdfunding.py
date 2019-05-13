from django import template

from ..models import Crowdfunding
from ..forms import (
    can_start_crowdfunding, get_editable_crowdfunding, ContributionForm
)

register = template.Library()


def get_foirequest_crowdfunding(foirequest):
    crowdfundings = getattr(foirequest, '_crowdfundings', None)
    if crowdfundings is None:
        foirequest._crowdfundings = Crowdfunding.objects.filter(
            request=foirequest
        )
    return foirequest._crowdfundings


@register.filter
def get_crowdfundings(foirequest, status=None):
    crowdfundings = get_foirequest_crowdfunding(foirequest)
    if status is not None:
        return [c for c in crowdfundings if c.status == status]
    return crowdfundings


@register.filter(name='can_start_crowdfunding')
def can_start_crowdfunding_filter(foirequest):
    crowdfundings = get_foirequest_crowdfunding(foirequest)
    return can_start_crowdfunding(crowdfundings)


@register.filter(name='get_editable_crowdfunding')
def get_editable_crowdfunding_filter(foirequest):
    crowdfundings = get_foirequest_crowdfunding(foirequest)
    return get_editable_crowdfunding(crowdfundings)


@register.filter
def get_crowdfunding_form(user):
    if user.is_authenticated:
        return ContributionForm(user=user)
    return ContributionForm()
