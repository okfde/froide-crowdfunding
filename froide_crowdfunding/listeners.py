from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from froide_payment.models import PaymentStatus

from froide.helper.email_sending import send_template_email

from . import contribution_successful
from .models import Contribution


def payment_status_changed(sender=None, instance=None, **kwargs):
    order = instance.order
    obj = order.get_domain_object()
    if not isinstance(obj, Contribution):
        return

    if instance.status == PaymentStatus.CONFIRMED:
        if obj.order.is_fully_paid():
            obj.status = 'success'
            contribution_successful.send(
                sender=Contribution, contribution=obj
            )
        else:
            obj.status = 'pending'
    elif instance.status in (
            PaymentStatus.ERROR, PaymentStatus.REFUNDED,
            PaymentStatus.REJECTED):
        obj.status = 'failed'
    elif instance.status == PaymentStatus.INPUT:
        obj.status = 'pending'
    obj.save()

    crowdfunding = obj.crowdfunding
    crowdfunding.update_amount_raised()


def send_contribution_notification(sender=None, contribution=None, **kawrgs):
    if contribution is None:
        return
    order = contribution.order
    if order is None:
        return
    email = order.user_email
    send_template_email(
        user=contribution.user,
        email=email,
        subject=_(
            '💸 Your crowdfunding contribution has been received'
        ),
        template='froide_crowdfunding/emails/contribution_received.txt',
        context={
            'crowdfunding': contribution.crowdfunding,
            'user': order.get_user_or_order(),
            'url': settings.SITE_URL + order.get_absolute_url(),
            'site_name': settings.SITE_NAME
        }
    )
