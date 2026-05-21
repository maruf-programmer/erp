from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AdmissionApplicationForm,
    AssignmentForm,
    CourseForm,
    GradeForm,
    GroupForm,
    SalaryForm,
    SubmissionForm,
    ProfileForm,
    UserCreateForm,
    UserUpdateForm,
)
from .models import AdmissionApplication, Assignment, Course, Group, Salary, Submission, User


def admin_required(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def can_manage_group(user, group):
    return admin_required(user) or group.teacher_id == user.id or group.assistants.filter(id=user.id).exists()


def home(request):
    featured_teachers = User.objects.filter(role=User.Role.TEACHER).order_by('first_name')[:4]
    best_students = User.objects.filter(role=User.Role.STUDENT).order_by('first_name')[:4]
    context = {
        'courses_count': Course.objects.filter(is_active=True).count() or 12,
        'teachers_count': User.objects.filter(role=User.Role.TEACHER).count() or 28,
        'students_count': User.objects.filter(role=User.Role.STUDENT).count() or 10000,
        'groups_count': Group.objects.filter(is_active=True).count() or 86,
        'featured_teachers': featured_teachers,
        'best_students': best_students,
    }
    return render(request, 'academy/home.html', context)


def apply_admission(request):
    form = AdmissionApplicationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Arizangiz qabul qilindi. Tez orada operatorimiz bog‘lanadi.')
        return redirect('home')
    return render(request, 'academy/application_form.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    if admin_required(user):
        groups = Group.objects.select_related('course', 'teacher').all()
        assignments = Assignment.objects.select_related('group', 'author').order_by('-created_at')[:8]
    elif user.role == User.Role.TEACHER:
        groups = user.teaching_groups.select_related('course', 'teacher').all()
        assignments = Assignment.objects.filter(group__teacher=user).select_related('group', 'author')[:8]
    elif user.role == User.Role.ASSISTANT:
        groups = user.assistant_groups.select_related('course', 'teacher').all()
        assignments = Assignment.objects.filter(group__assistants=user).select_related('group', 'author')[:8]
    else:
        groups = user.student_groups.select_related('course', 'teacher').all()
        assignments = Assignment.objects.filter(group__students=user).select_related('group', 'author').order_by('-created_at')[:8]

    context = {
        'users_count': User.objects.count(),
        'courses_count': Course.objects.count(),
        'groups_count': groups.count(),
        'submissions_count': Submission.objects.count() if admin_required(user) else Submission.objects.filter(student=user).count(),
        'groups': groups.annotate(student_count=Count('students')),
        'assignments': assignments,
        'salaries': Salary.objects.filter(employee=user).order_by('-month')[:4],
    }
    return render(request, 'academy/dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil yangilandi.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'academy/form.html', {'form': form, 'title': 'Mening profilim'})


@login_required
def user_list(request):
    if not admin_required(request.user):
        raise PermissionDenied
    users = User.objects.order_by('role', 'first_name', 'username')
    return render(request, 'academy/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not admin_required(request.user):
        raise PermissionDenied
    form = UserCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Yangi foydalanuvchi yaratildi.')
        return redirect('user_list')
    return render(request, 'academy/form.html', {'form': form, 'title': 'Foydalanuvchi qo‘shish'})


@login_required
def user_edit(request, pk):
    if not admin_required(request.user):
        raise PermissionDenied
    target = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=target)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Foydalanuvchi ma’lumotlari yangilandi.')
        return redirect('user_list')
    return render(request, 'academy/form.html', {'form': form, 'title': 'Foydalanuvchini tahrirlash'})


@login_required
def course_create(request):
    if not admin_required(request.user):
        raise PermissionDenied
    return save_form(request, CourseForm, 'Kurs qo‘shish', 'dashboard')


@login_required
def group_create(request):
    if not admin_required(request.user):
        raise PermissionDenied
    return save_form(request, GroupForm, 'Guruh ochish', 'dashboard')


@login_required
def assignment_create(request):
    form = AssignmentForm(request.POST or None, request.FILES or None)
    if not admin_required(request.user):
        allowed_groups = Group.objects.filter(teacher=request.user) | Group.objects.filter(assistants=request.user)
        form.fields['group'].queryset = allowed_groups.distinct()
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        if not can_manage_group(request.user, assignment.group):
            raise PermissionDenied
        assignment.author = request.user
        assignment.save()
        messages.success(request, 'Vazifa yoki imtihon joylandi.')
        return redirect('assignment_detail', pk=assignment.pk)
    return render(request, 'academy/form.html', {'form': form, 'title': 'Vazifa / imtihon berish'})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('group', 'author'), pk=pk)
    is_student = request.user.role == User.Role.STUDENT
    if is_student and not assignment.group.students.filter(id=request.user.id).exists():
        raise PermissionDenied
    if not is_student and not can_manage_group(request.user, assignment.group):
        raise PermissionDenied

    submission_form = None
    if is_student:
        submission, _ = Submission.objects.get_or_create(assignment=assignment, student=request.user)
        submission_form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission)
        if request.method == 'POST' and submission_form.is_valid():
            submission_form.save()
            messages.success(request, 'Ishingiz tizimga yuklandi.')
            return redirect('assignment_detail', pk=assignment.pk)

    return render(request, 'academy/assignment_detail.html', {
        'assignment': assignment,
        'submission_form': submission_form,
        'submissions': assignment.submissions.select_related('student').all(),
    })


@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission.objects.select_related('assignment__group'), pk=pk)
    if not can_manage_group(request.user, submission.assignment.group):
        raise PermissionDenied
    form = GradeForm(request.POST or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Baho va izoh saqlandi.')
        return redirect('assignment_detail', pk=submission.assignment_id)
    return render(request, 'academy/form.html', {'form': form, 'title': 'Ishni baholash'})


@login_required
def salary_create(request):
    if not admin_required(request.user):
        raise PermissionDenied
    return save_form(request, SalaryForm, 'Oylik chiqarish', 'dashboard')


def save_form(request, form_class, title, redirect_to):
    form = form_class(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ma’lumot saqlandi.')
        return redirect(redirect_to)
    return render(request, 'academy/form.html', {'form': form, 'title': title})
