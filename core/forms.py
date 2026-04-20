from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Property, Unit, Tenant, Payment, Announcement, MaintenanceRequest, Agreement
from datetime import date


class LandlordRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'address', 'city', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Green Apartments'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_number', 'unit_type', 'floor', 'size_sqft', 'rent_amount', 'status', 'available_from', 'description']
        widgets = {
            'unit_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A1, 101'}),
            'unit_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Studio, 1 Bedroom'}),
            'floor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ground, 1st'}),
            'size_sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'national_id',
            'unit', 'move_in_date', 'move_out_date', 'rent_amount',
            'rent_due_day', 'deposit_amount', 'deposit_paid', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XX XXX XXX'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'move_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'move_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rent_due_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 28}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deposit_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, landlord=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord:
            # Only show units from this landlord's properties
            self.fields['unit'].queryset = Unit.objects.filter(
                prop__landlord=landlord
            )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'tenant', 'amount_expected', 'amount_paid', 'period_month', 'period_year',
            'due_date', 'date_paid', 'payment_method', 'mpesa_transaction_code', 'notes'
        ]
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'amount_expected': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'period_month': forms.Select(
                choices=[(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
                attrs={'class': 'form-select'}
            ),
            'period_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2099}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_paid': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'mpesa_transaction_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. QHJ9K3PLMN'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, landlord=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord:
            self.fields['tenant'].queryset = Tenant.objects.filter(landlord=landlord, is_active=True)
        today = date.today()
        if not self.instance.pk:
            self.fields['period_month'].initial = today.month
            self.fields['period_year'].initial = today.year


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'audience', 'property', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'audience': forms.Select(attrs={'class': 'form-select', 'id': 'audienceSelect'}),
            'property': forms.Select(attrs={'class': 'form-select', 'id': 'propertySelect'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, landlord=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord:
            self.fields['property'].queryset = Property.objects.filter(landlord=landlord)
        self.fields['property'].required = False


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['unit', 'tenant', 'title', 'description', 'priority', 'status', 'reported_date', 'resolution_notes']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reported_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, landlord=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if landlord:
            self.fields['unit'].queryset = Unit.objects.filter(prop__landlord=landlord)
            self.fields['tenant'].queryset = Tenant.objects.filter(landlord=landlord, is_active=True)
        self.fields['tenant'].required = False


class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement
        fields = ['title', 'agreement_type', 'description', 'document', 'content', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'agreement_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
