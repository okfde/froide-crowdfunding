import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import mail_managers
from django.db.models import BooleanField, Case, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from froide.foirequest.auth import can_write_foirequest
from froide.foirequest.models import FoiRequest
from froide.helper.email_sending import send_template_email
from froide.helper.utils import render_403

from .forms import (
    ContributionForm,
    CrowdfundingRequestStartForm,
    DonationContributionForm,
)
from .models import Crowdfunding

logger = logging.getLogger(__name__)


class CrowdfundingListView(LoginRequiredMixin, ListView):
    template_name = "froide_crowdfunding/list.html"

    def get_queryset(self):
        return Crowdfunding.objects.filter(user=self.request.user)


class CrowdfundingDetailView(DetailView):
    template_name = "froide_crowdfunding/detail.html"

    def get_queryset(self):
        return Crowdfunding.objects.filter(status__in=Crowdfunding.PUBLIC_STATUS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contributions"] = (
            self.object.contribution_set.annotate(
                mine=Case(
                    When(
                        user__isnull=False,
                        user_id=self.request.user.id,
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .filter(Q(mine=True) | Q(status="success"))
            .order_by("-mine", "-timestamp")
        )
        return context


def request_crowdfunding(request, pk):
    foirequest = get_object_or_404(FoiRequest, pk=pk)
    if not can_write_foirequest(foirequest, request):
        return render_403(request)

    if request.method == "POST":
        form = CrowdfundingRequestStartForm(
            data=request.POST, user=request.user, foirequest=foirequest
        )
        if form.is_valid():
            obj = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Your crowdfunding campaign " "has been submitted for approval."),
            )
            context = {
                "user": obj.user,
                "crowdfunding": obj,
                "site_name": settings.SITE_NAME,
            }
            send_template_email(
                user=obj.user,
                subject=_("💸 Your crowdfunding project has been created"),
                template="froide_crowdfunding/emails/needs_approval.txt",
                context=context,
            )
            mail_managers(
                _("Crowdfunding project needs approval"),
                settings.SITE_URL
                + reverse(
                    "admin:froide_crowdfunding_crowdfunding_change", args=(obj.pk,)
                ),
            )
            return redirect(foirequest)
        else:
            messages.add_message(
                request, messages.ERROR, _("Your form contained errors.")
            )
    else:
        form = CrowdfundingRequestStartForm(user=request.user, foirequest=foirequest)
    return render(
        request,
        "froide_crowdfunding/request_crowdfunding.html",
        context={
            "crowdfunding_form": form,
            "object": foirequest,
        },
    )


def start_contribution(request, pk, form_class=ContributionForm, extra_context=None):
    crowdfunding = get_object_or_404(Crowdfunding, pk=pk)
    if crowdfunding.status != "running":
        return redirect(crowdfunding)

    user = None
    if request.user.is_authenticated:
        user = request.user

    form_kwargs = {"crowdfunding": crowdfunding, "user": user}
    status = 200
    if request.method == "POST":
        form = form_class(data=request.POST, **form_kwargs)

        if form.is_valid():
            order, contribution = form.save()
            data = form.cleaned_data
            payment_url = order.get_absolute_payment_url(data["method"])
            return redirect(payment_url)
        status = 400
    else:
        form = form_class(**form_kwargs)

    context = {
        "form": form,
        "crowdfunding_contribute_urlname": (
            "crowdfunding:crowdfunding-start_contribution"
        ),
        "crowdfunding": crowdfunding,
    }

    if extra_context is not None:
        context.update(extra_context)

    return render(
        request, "froide_crowdfunding/contribute.html", context, status=status
    )


def start_contribution_donation(request, pk):
    extra_context = {}
    extra_context[
        "crowdfunding_contribute_urlname"
    ] = "crowdfunding:crowdfunding-start_contribution_donation"
    return start_contribution(
        request, pk, form_class=DonationContributionForm, extra_context=extra_context
    )
