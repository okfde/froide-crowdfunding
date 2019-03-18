from payments import PaymentStatus

from .models import Contribution


def payment_status_changed(sender=None, instance=None, **kwargs):
    order = instance.order
    obj = order.get_domain_object()
    if not isinstance(obj, Contribution):
        return

    if instance.status == PaymentStatus.CONFIRMED:
        if obj.order.is_fully_paid():
            obj.status = 'success'
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
