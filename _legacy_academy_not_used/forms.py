from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import AdmissionApplication, Assignment, Course, Group, Salary, Submission, User


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'checkbox')
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs.setdefault('class', 'input multi')
            else:
                widget.attrs.setdefault('class', 'input')


class UserCreateForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'role',
            'phone', 'passport_number', 'birth_date', 'address', 'photo',
            'bio', 'password1', 'password2',
        ]
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}


class UserUpdateForm(StyledFormMixin, forms.ModelForm):
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


class AssignmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'kind', 'group', 'description', 'file', 'deadline']
        widgets = {'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class SubmissionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['text', 'file']


class GradeForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['score', 'feedback']


class SalaryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'
        widgets = {'month': forms.DateInput(attrs={'type': 'date'})}


class AdmissionApplicationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = ['full_name', 'phone', 'course', 'age', 'message']
        labels = {
            'full_name': 'Ism familiya',
            'phone': 'Telefon raqam',
            'course': 'Qaysi kursga qiziqyapsiz?',
            'age': 'Yosh',
            'message': 'Qo‘shimcha izoh',
        }
        widgets = {
            'course': forms.TextInput(attrs={'placeholder': 'Python, Frontend, Grafik dizayn...'}),
            'message': forms.Textarea(attrs={'placeholder': 'Qaysi vaqtda o‘qimoqchisiz?'}),
        }
