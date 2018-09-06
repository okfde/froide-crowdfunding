from payments import PaymentStatus

from .models import Contribution


TRIGGERS = (PaymentStatus.CONFIRMED, PaymentStatus.REFUNDED)


def payment_status_changed(sender=None, instance=None, **kwargs):
    if instance.status not in TRIGGERS:
        return

    order = instance.order
    obj = order.get_domain_object()
    if not isinstance(obj, Contribution):
        return

    crowdfunding = obj.crowdfunding
    crowdfunding.update_amount_raised()
