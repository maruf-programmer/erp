from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            classes = widget.attrs.get('class', '').split()
            if isinstance(widget, forms.CheckboxInput):
                classes.append('checkbox')
            elif isinstance(widget, forms.SelectMultiple):
                classes.append('input')
                classes.append('multi')
            else:
                classes.append('input')
            if self.errors.get(name):
                classes.append('invalid')
            widget.attrs['class'] = ' '.join(sorted(set(classes))).strip()


class UserCreateForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'role',
            'phone', 'passport_number', 'birth_date', 'address', 'photo',
            'bio', 'password1', 'password2',
        ]
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Bu email manzil allaqachon ishlatilgan. Iltimos boshqasini kiriting.')
        return email


class UserUpdateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role', 'phone',
            'passport_number', 'birth_date', 'address', 'photo', 'bio',
        ]
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Bu email manzil allaqachon ishlatilgan. Iltimos boshqasini kiriting.')
        return email
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role', 'phone',
            'passport_number', 'birth_date', 'address', 'photo', 'bio',
        ]
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'passport_number', 'birth_date', 'address', 'photo', 'bio',
        ]
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}
