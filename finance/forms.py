from accounts.forms import StyledFormMixin
from django import forms

from .models import Salary


class SalaryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'
        widgets = {'month': forms.DateInput(attrs={'type': 'date'})}
