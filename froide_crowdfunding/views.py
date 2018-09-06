import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin

from froide.foirequest.models import FoiRequest
from froide.foirequest.auth import can_write_foirequest
from froide.foirequest.views.request import show_foirequest
from froide.helper.utils import render_403

from .models import Crowdfunding
from .forms import (
    CrowdfundingRequestStartForm, ContributionForm
)


logger = logging.getLogger(__name__)


class CrowdfundingListView(UserPassesTestMixin, ListView):
    template_name = 'froide_crowdfunding/list.html'

    def get_test_func(self):
        return lambda: self.request.user.is_staff

    def get_queryset(self):
        return Crowdfunding.objects.filter(
            status='running'
        )


@require_POST
def request_crowdfunding(request, pk):
    foirequest = get_object_or_404(FoiRequest, pk=pk)
    if not can_write_foirequest(foirequest, request):
        return render_403(request)

    crowdfundings = Crowdfunding.objects.filter(request=foirequest)
    form = CrowdfundingRequestStartForm(
        data=request.POST, crowdfundings=crowdfundings,
        user=request.user, foirequest=foirequest
    )
    if form.is_valid():
        form.save()
        messages.add_message(
            request, messages.SUCCESS,
            _('Your crowdfunding campaign has been submitted for approval.')
        )
        return redirect(foirequest)
    messages.add_message(
        request, messages.ERROR,
        _('Your form contained errors.')
    )
    return show_foirequest(request, foirequest, context={
        "crowdfunding_form": form,
        'active_tab': 'crowdfunding'
    }, status=400)


def start_contribution(request, pk):
    crowdfunding = get_object_or_404(Crowdfunding, pk=pk)
    if crowdfunding.status != 'running':
        return render_403(request)

    user = None
    if request.user.is_authenticated:
        user = request.user

    form_kwargs = {
        'crowdfunding': crowdfunding,
        'user': user
    }

    if request.method == 'POST':
        form = ContributionForm(data=request.POST, **form_kwargs)

        if form.is_valid():
            contribution = form.save()
            data = form.cleaned_data
            return redirect(reverse('froide_payment:start-payment', kwargs={
                'token': contribution.order.token,
                'variant': data['method']
            }))
    else:
        form = ContributionForm(**form_kwargs)

    return render(request, 'froide_crowdfunding/contribute.html', {
        'form': form,
        'crowdfunding': crowdfunding
    }, status=400)
