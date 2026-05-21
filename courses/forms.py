from accounts.forms import StyledFormMixin
from django import forms

from .models import Course, Group


class CourseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'


class GroupForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'lesson_time': forms.TimeInput(attrs={'type': 'time'}),
        }
