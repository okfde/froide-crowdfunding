from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from froide.foirequest.models import FoiRequest


OVERHEAD_FACTOR = Decimal('1.15')


class Crowdfunding(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    STATUS_CHOICES = (
        ('needs_approval', _('needs approval')),
        ('denied', _('denied')),
        ('running', _('running')),
        ('finished', _('finished')),
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='needs_approval'
    )
    KIND_CHOICES = (
        ('fees', _('fees')),
        ('appeal', _('appeal')),
        ('lawsuit', _('lawsuit')),
        ('other', _('other')),
    )
    kind = models.CharField(
        max_length=25,
        choices=KIND_CHOICES,
    )

    date_requested = models.DateTimeField(
        default=timezone.now, null=True, blank=True
    )
    date_approved = models.DateTimeField(null=True, blank=True)
    date_end = models.DateTimeField(null=True, blank=True)

    amount_requested = models.DecimalField(
        decimal_places=2, max_digits=10
    )
    amount_needed = models.DecimalField(
        decimal_places=2, max_digits=10
    )
    amount_raised = models.DecimalField(
        decimal_places=2, max_digits=10,
        default=Decimal(0.0)
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    request = models.ForeignKey(
        FoiRequest, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('-date_requested',)
        get_latest_by = 'date_requested'
        verbose_name = _('Crowdfunding')
        verbose_name_plural = _('Crowdfundings')

    def __str__(self):
        return 'Crowdfunding "%s" (#%s)' % (self.title, self.pk)

    @property
    def progress_percent(self):
        if self.amount_needed == 0:
            return 0
        return min(int(self.amount_raised / self.amount_needed * 100), 100)

    def get_absolute_url(self):
        return reverse('crowdfunding:crowdfunding-detail',
                       kwargs={'slug': self.slug})

    def get_start_contribution_url(self):
        return reverse('crowdfunding:crowdfunding-start_contribution',
                       kwargs={'pk': self.pk})

    def update_amount_raised(self, save=True):
        contributions = self.contribution_set.all().select_related('order')
        amount = Decimal(0)
        for contribution in contributions:
            if not contribution.order:
                continue
            if contribution.order.is_fully_paid():
                amount += contribution.amount
        self.amount_raised = amount
        if save:
            self.save()


class Contribution(models.Model):
    crowdfunding = models.ForeignKey(
        Crowdfunding,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    timestamp = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    note = models.TextField(blank=True)
    public = models.BooleanField(default=False)
    order = models.OneToOneField(
        'froide_payment.Order', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    STATUS_CHOICES = (
        ('', _('Waiting for input')),
        ('pending', _('Processing...')),
        ('success', _('Successful')),
        ('failed', _('Failed')),
    )
    STATUS_COLORS = {
        '': 'secondary',
        'pending': 'light',
        'success': 'success',
        'failed': 'danger',
    }
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=''
    )

    class Meta:
        ordering = ('-timestamp',)
        get_latest_by = 'timestamp'
        verbose_name = _('Contribution')
        verbose_name_plural = _('Contributions')

    def __str__(self):
        return 'Contribution %s' % self.pk

    def get_absolute_url(self):
        return self.order.get_absolute_url()

    def get_finish_url(self, state='success'):
        return '{}?result={}'.format(
            self.get_absolute_url(),
            state,
        )

    def get_success_url(self):
        return self.get_finish_url('success')

    def get_failure_url(self):
        return self.get_finish_url('failure')

    @property
    def status_color(self):
        return self.STATUS_COLORS[self.status]
