import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from froide.helper.widgets import PriceInput
from froide.helper.db_utils import save_obj_with_slug

from froide_payment.models import Order, PAYMENT_METHODS

from .models import OVERHEAD_FACTOR, Crowdfunding, Contribution


def can_start_crowdfunding(crowdfundings):
    if any(c.status != 'finished' for c in crowdfundings):
        return False
    return True


POSTCODE_RE = re.compile('(\d{5})\s+(.*)')


def parse_address(address):
    match = POSTCODE_RE.search(address)
    if match is None:
        return {}
    postcode = match.group(1)
    city = match.group(2)
    refined = address.replace(match.group(0), '').strip().splitlines()
    return {
        'address': refined[0],
        'postcode': postcode,
        'city': city
    }


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
        help_text=_('What area of your request would you like to crowdfund?')
    )

    description = forms.CharField(
        label=_('Description'),
        help_text=_(
            'Describe why getting the information is important and '
            'why people should help.'),
        widget=forms.Textarea(attrs={
            'class': 'form-control'
        })
    )

    amount_requested = forms.FloatField(
        label=_("Amount"),
        initial=0.0,
        required=True, min_value=10,
        localize=True,
        widget=PriceInput,
        help_text=_('Please specify the amount you need to raise'
                    ' (minimum 10 Euro).')
    )

    class Meta:
        model = Crowdfunding
        fields = ('title', 'kind', 'description', 'amount_requested',)

    def __init__(self, *args, **kwargs):
        self.foirequest = kwargs.pop('foirequest', None)
        self.crowdfundings = kwargs.pop('crowdfundings', None)
        self.user = kwargs.pop('user', None)
        super(CrowdfundingRequestStartForm, self).__init__(*args, **kwargs)

        if self.foirequest is not None:
            self.fields['title'].initial = self.foirequest.title
        if self.foirequest.costs:
            self.fields['amount_requested'].initial = self.foirequest.costs
        if self.crowdfundings is not None:
            existing_kinds = set(c.kind for c in self.crowdfundings)
            self.fields['kind'].choices = [
                c for c in Crowdfunding.KIND_CHOICES
                if c[0] not in existing_kinds
            ]

    def clean(self):
        if not can_start_crowdfunding(self.crowdfundings):
            raise forms.ValidationError(_('You have an ongoing crowdfunding.'))
        return self.cleaned_data

    def save(self, **kwargs):
        kwargs['commit'] = False
        crowdfunding = super(CrowdfundingRequestStartForm, self).save(**kwargs)
        crowdfunding.user = self.user
        crowdfunding.request = self.foirequest
        amount_needed = crowdfunding.amount_requested * OVERHEAD_FACTOR
        crowdfunding.amount_needed = amount_needed
        save_obj_with_slug(crowdfunding)
        return crowdfunding


class ContributionForm(forms.Form):
    amount = forms.FloatField(
        label=_("Amount"),
        initial=10.0,
        required=True, min_value=1,
        localize=True,
        widget=PriceInput,
        help_text=_('Please specify the amount you want to contribute.')
    )

    note = forms.CharField(
        label=_('Note'),
        required=False,
        help_text=_(
            'Leave an optional public note why you are '
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

    email = forms.CharField(
        max_length=255,
        label=_('Email'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Your email address'),
            'class': 'form-control'
        })
    )

    method = forms.ChoiceField(
        label=_('Payment method'),
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect,
        initial=PAYMENT_METHODS[0][0]
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
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

    def save(self):
        d = self.cleaned_data
        address_lines = d['address'].splitlines()

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
            note=self.cleaned_data['note'],
            order=order
        )
        return contribution
