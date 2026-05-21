from accounts.forms import StyledFormMixin
from django import forms

from .models import AdmissionApplication


class AdmissionApplicationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = ['full_name', 'phone', 'application_type', 'course', 'age', 'message']
        labels = {
            'full_name': 'Ism familiya',
            'phone': 'Telefon raqam',
            'application_type': 'Ariza turi',
            'course': 'Qaysi kursga qiziqyapsiz?',
            'age': 'Yosh',
            'message': 'Qo‘shimcha izoh',
        }
        widgets = {
            'application_type': forms.Select(choices=[
                ('O‘quvchi arizasi', 'O‘quvchi bo‘lib o‘qish'),
                ('O‘qituvchi arizasi', 'O‘qituvchi bo‘lib ishlash'),
                ('Hamkorlik arizasi', 'Hamkorlik'),
                ('Boshqa ariza', 'Boshqa'),
            ]),
            'course': forms.TextInput(attrs={'placeholder': 'Python, Frontend, Grafik dizayn...'}),
            'message': forms.Textarea(attrs={'placeholder': 'Qaysi vaqtda o‘qimoqchisiz?'}),
        }
