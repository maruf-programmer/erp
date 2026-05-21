from accounts.forms import StyledFormMixin
from django import forms

from .models import Assignment, Submission


class AssignmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'kind', 'group', 'description', 'file', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'placeholder': 'Vazifa matnini yozing...'}),
        }
        labels = {
            'description': 'Matn',
            'file': 'Fayl',
            'deadline': 'Topshirish muddati',
        }


class SubmissionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['text', 'file']
        widgets = {'text': forms.Textarea(attrs={'placeholder': 'Javobingizni yozing...'})}
        labels = {'text': 'Javob matni', 'file': 'Fayl'}


class GradeForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['status', 'score', 'silver_coins', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'placeholder': 'O‘quvchiga izoh yozing...'}),
        }
        labels = {
            'status': 'Holat',
            'score': 'Ball',
            'silver_coins': 'Kumush tanga',
            'feedback': 'Izoh',
        }
