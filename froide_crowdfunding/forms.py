from decimal import Decimal
import math

from django import forms
from django.utils.translation import ugettext_lazy as _

from froide.account.utils import parse_address
from froide.account.forms import user_extra_registry
from froide.helper.widgets import BootstrapCheckboxInput, PriceInput
from froide.helper.db_utils import save_obj_with_slug

from froide_payment.models import Order, CHECKOUT_PAYMENT_CHOICES_DICT

from .models import OVERHEAD_FACTOR, Crowdfunding, Contribution


CROWDFUNDING_METHODS = (
    'creditcard', 'sepa', 'paypal', 'sofort'
)

PAYMENT_METHODS = [
    (method, CHECKOUT_PAYMENT_CHOICES_DICT[method])
    for method in CROWDFUNDING_METHODS
]


def can_start_crowdfunding(crowdfundings):
    if all(c.status in Crowdfunding.FINAL_STATUS for c in crowdfundings):
        return True
    return False


def get_editable_crowdfunding(crowdfundings):
    editable = [
        c for c in crowdfundings
        if c.status in Crowdfunding.REVIEW_STATUS
    ]
    if not editable:
        return None
    if len(editable) > 1:
        return None
    return editable[0]


def calculate_amount_needed(amount_requested):
    amount_needed = amount_requested * OVERHEAD_FACTOR
    # Round up to next 10
    amount_needed = math.ceil(amount_needed / 10) * 10
    return Decimal(amount_needed)


class CrowdfundingRequestStartForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        label=_('Title'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Title of campaign'),
            'class': 'form-control'
        })
    )

    kind = forms.ChoiceField(
        label=_('Kind of costs'),
        choices=Crowdfunding.KIND_CHOICES,
        help_text=_('What area of your request would you like to crowdfund?')
    )

    description = forms.CharField(
        label=_('What is your interest in this information?'),
        help_text=_(
            'Describe why getting the information is important '
            'to you.'),
        widget=forms.Textarea(attrs={
            'class': 'form-control'
        })
    )

    public_interest = forms.CharField(
        label=_('Why is this important to the public?'),
        help_text=_(
            'Describe how this case affects the public.'),
        widget=forms.Textarea(attrs={
            'class': 'form-control'
        })
    )

    amount_requested = forms.DecimalField(
        label=_("Amount"),
        initial=10,
        required=True, min_value=10,
        decimal_places=2,
        max_digits=10,
        localize=True,
        widget=PriceInput,
        help_text=_('Please specify the amount you need to raise '
                    '(minimum 10 Euro). We will increase this amount to '
                    'cover our own costs.')
    )

    terms = forms.BooleanField(
        widget=BootstrapCheckboxInput,
        required=True,
        label=_('Accept our terms for crowdfunding.'),
        error_messages={
            'required': _(
                'You need to accept our crowdfunding terms.'
            )},
    )

    class Meta:
        model = Crowdfunding
        fields = (
            'title', 'kind', 'description', 'public_interest',
            'amount_requested',
        )

    def __init__(self, *args, **kwargs):
        self.foirequest = kwargs.pop('foirequest', None)

        self.crowdfundings = Crowdfunding.objects.filter(
            request=self.foirequest
        )
        kwargs['instance'] = get_editable_crowdfunding(self.crowdfundings)
        self.user = kwargs.pop('user', None)
        super(CrowdfundingRequestStartForm, self).__init__(*args, **kwargs)

        if self.foirequest is not None:
            self.fields['title'].initial = self.foirequest.title
        if self.foirequest.costs:
            self.fields['amount_requested'].initial = self.foirequest.costs

    def clean(self):
        can_start = can_start_crowdfunding(self.crowdfundings)
        if not self.instance and not can_start:
            raise forms.ValidationError(_('You have an ongoing crowdfunding.'))
        return self.cleaned_data

    def save(self, **kwargs):
        kwargs['commit'] = False
        crowdfunding = super(CrowdfundingRequestStartForm, self).save(**kwargs)
        crowdfunding.user = self.user
        crowdfunding.request = self.foirequest
        # Calculate amount needed
        crowdfunding.amount_needed = calculate_amount_needed(
            crowdfunding.amount_requested
        )
        crowdfunding.status = 'needs_approval'
        if crowdfunding.slug:

            crowdfunding.save()
        else:
            save_obj_with_slug(crowdfunding)
        return crowdfunding


class ContributionForm(forms.Form):
    amount = forms.DecimalField(
        label=_("Amount"),
        initial=10.0,
        required=True, min_value=1,
        decimal_places=2,
        max_digits=10,
        localize=True,
        widget=PriceInput,
        help_text=_('Please specify the amount you want to contribute.')
    )

    note = forms.CharField(
        label=_('Note'),
        required=False,
        max_length=260,
        help_text=_(
            'Leave an optional public note (260 chars) why you are '
            'supporting this crowdfunding.'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )

    first_name = forms.CharField(
        max_length=255,
        label=_('First name'),
        widget=forms.TextInput(attrs={
            'placeholder': _('First name'),
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=255,
        label=_('Last name'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Last name'),
            'class': 'form-control'
        })
    )
    public = forms.BooleanField(
        required=False,
        label=_('Show my name as a public contributor'),
        widget=BootstrapCheckboxInput
    )
    address = forms.CharField(
        max_length=255,
        label=_('Address'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Address'),
            'class': 'form-control'
        })
    )
    postcode = forms.CharField(
        max_length=255,
        label=_('Postcode'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Postcode'),
            'class': 'form-control'
        })
    )
    city = forms.CharField(
        max_length=255,
        label=_('City'),
        widget=forms.TextInput(attrs={
            'placeholder': _('City'),
            'class': 'form-control'
        })
    )
    country = forms.ChoiceField(
        label=_('Country'),
        choices=(
            ('DE', _('Germany')),
            ('AT', _('Austria')),
            ('CH', _('Switzerland')),
        ),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    email = forms.EmailField(
        max_length=255,
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    method = forms.ChoiceField(
        label=_('Payment method'),
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect,
        initial=PAYMENT_METHODS[0][0]
    )

    terms = forms.BooleanField(
        widget=BootstrapCheckboxInput,
        required=True,
        label=_('Accept our terms for crowdfunding.'),
        error_messages={
            'required': _(
                'You need to accept our Terms '
                'and Conditions and Priavcy Statement.'
            )},
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user is not None and not user.is_authenticated:
            user = None
        self.user = user
        self.crowdfunding = kwargs.pop('crowdfunding', None)
        super(ContributionForm, self).__init__(*args, **kwargs)

        if self.user is not None:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            parsed = parse_address(self.user.address)
            self.fields['address'].initial = parsed.get('address', '')
            self.fields['postcode'].initial = parsed.get('postcode', '')
            self.fields['city'].initial = parsed.get('city', '')
        user_extra_registry.on_init('donation', self)

    def clean(self):
        user_extra_registry.on_clean('donation', self)
        return self.cleaned_data

    def save(self):
        user_extra_registry.on_save(
            'donation', self,
            self.user if self.user and self.user.is_authenticated else None
        )

        d = self.cleaned_data
        address_lines = d['address'].splitlines() or ['']

        order = Order.objects.create(
            user=self.user,
            first_name=d['first_name'],
            last_name=d['last_name'],
            street_address_1=address_lines[0],
            street_address_2='\n'.join(address_lines[1:]),
            city=d['city'],
            postcode=d['postcode'],
            country=d['country'],
            user_email=d['email'],
            total_net=d['amount'],
            total_gross=d['amount'],
            is_donation=True,
            kind='froide_crowdfunding.Contribution',
            description=_('Contribution to Crowdfunding “{}”').format(
                self.crowdfunding.title
            )
        )
        contribution = Contribution.objects.create(
            crowdfunding=self.crowdfunding,
            user=self.user,
            amount=self.cleaned_data['amount'],
            note=self.cleaned_data.get('note', ''),
            public=self.cleaned_data.get('public', False),
            order=order,
        )
        return order, contribution


class DonationContributionForm(ContributionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('note')
        self.fields.pop('terms')
