import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import mail_managers
from django.urls import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Case, When, Value, BooleanField, Q

from froide.foirequest.models import FoiRequest
from froide.foirequest.auth import can_write_foirequest
from froide.helper.utils import render_403
from froide.helper.email_sending import send_template_email

from .models import Crowdfunding
from .forms import (
    CrowdfundingRequestStartForm, ContributionForm
)


logger = logging.getLogger(__name__)


class CrowdfundingListView(ListView):
    template_name = 'froide_crowdfunding/list.html'

    def get_queryset(self):
        return Crowdfunding.objects.filter(
            status='running'
        )


class CrowdfundingDetailView(DetailView):
    template_name = 'froide_crowdfunding/detail.html'

    def get_queryset(self):
        return Crowdfunding.objects.filter(
            Q(status='running') | Q(status='finished')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contributions'] = self.object.contribution_set.annotate(
            mine=Case(
                When(user_id=self.request.user.id, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).filter(
            Q(mine=True) | Q(status='success')
        ).order_by('-mine', '-timestamp')
        return context


def request_crowdfunding(request, pk):
    foirequest = get_object_or_404(FoiRequest, pk=pk)
    if not can_write_foirequest(foirequest, request):
        return render_403(request)

    if request.method == 'POST':
        form = CrowdfundingRequestStartForm(
            data=request.POST,
            user=request.user, foirequest=foirequest
        )
        if form.is_valid():
            obj = form.save()
            messages.add_message(
                request, messages.SUCCESS,
                _('Your crowdfunding campaign '
                  'has been submitted for approval.')
            )
            context = {
                'user': obj.user,
                'crowdfunding': obj,
                'site_name': settings.SITE_NAME,
            }
            send_template_email(
                user=obj.user,
                subject=_(
                    '💸 Your crowdfunding project has been created'
                ),
                template='froide_crowdfunding/emails/needs_approval.txt',
                context=context
            )
            mail_managers(
                _('Crowdfunding project needs approval'),
                settings.SITE_URL + reverse(
                    'admin:froide_crowdfunding_crowdfunding_change',
                    args=(obj.pk,)
                )
            )
            return redirect(foirequest)
        else:
            messages.add_message(
                request, messages.ERROR,
                _('Your form contained errors.')
            )
    else:
        form = CrowdfundingRequestStartForm(
            user=request.user, foirequest=foirequest
        )
    return render(
        request,
        'froide_crowdfunding/request_crowdfunding.html',
        context={
            "crowdfunding_form": form,
            'object': foirequest,
        }
    )


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
    status = 200
    if request.method == 'POST':
        form = ContributionForm(data=request.POST, **form_kwargs)

        if form.is_valid():
            contribution = form.save()
            data = form.cleaned_data
            return redirect(reverse('froide_payment:start-payment', kwargs={
                'token': contribution.order.token,
                'variant': data['method']
            }))
        status = 400
    else:
        form = ContributionForm(**form_kwargs)

    return render(request, 'froide_crowdfunding/contribute.html', {
        'form': form,
        'crowdfunding': crowdfunding
    }, status=status)
