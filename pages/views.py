import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Case, Count, IntegerField, Max, Q, Sum, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.activity import record_login_activity
from accounts.face_auth import compare_faces
from accounts.forms import ProfileForm, UserCreateForm, UserUpdateForm
from accounts.models import LoginActivity, User
from admissions.forms import AdmissionApplicationForm
from assignments.forms import AssignmentForm, GradeForm, SubmissionForm
from assignments.models import Assignment, Submission
from courses.forms import CourseForm, GroupForm
from courses.models import Course, Group
from finance.forms import SalaryForm
from finance.models import Salary
from .models import FeaturedPerson, HomePageSettings, VideoLesson


class RoleAwareLoginView(LoginView):
    template_name = 'academy/login.html'

    def form_valid(self, form):
        self.request.session.flush()
        return super().form_valid(form)


def admin_required(user):
    return user.is_superuser or user.role == User.Role.ADMIN


def can_manage_group(user, group):
    return admin_required(user) or group.teacher_id == user.id or group.assistants.filter(id=user.id).exists()


SUBMITTED_WORK_FILTER = Q(assignments__submissions__text__gt='') | Q(assignments__submissions__file__gt='')
PENDING_WORK_FILTER = (
    Q(assignments__submissions__status=Submission.Status.PENDING)
    & Q(assignments__submissions__teacher_seen_at__isnull=True)
    & SUBMITTED_WORK_FILTER
)


def home(request):
    settings = HomePageSettings.objects.first()
    teacher_cards = FeaturedPerson.objects.filter(kind__in=[FeaturedPerson.Kind.TEACHER, FeaturedPerson.Kind.TEACHER_OF_YEAR], is_active=True)[:4]
    best_students = FeaturedPerson.objects.filter(kind=FeaturedPerson.Kind.BEST_STUDENT, is_active=True)[:4]
    video_lessons = VideoLesson.objects.filter(is_active=True).select_related('teacher')[:3]
    context = {
        'home_settings': settings,
        'courses_count': Course.objects.filter(is_active=True).count() or (settings.courses_metric if settings else 12),
        'teachers_count': User.objects.filter(role=User.Role.TEACHER).count() or (settings.teachers_metric if settings else 28),
        'students_count': User.objects.filter(role=User.Role.STUDENT).count() or (settings.students_metric if settings else 10000),
        'groups_count': Group.objects.filter(is_active=True).count() or (settings.groups_metric if settings else 86),
        'featured_teachers': teacher_cards,
        'best_students': best_students,
        'teacher_of_year': FeaturedPerson.objects.filter(kind=FeaturedPerson.Kind.TEACHER_OF_YEAR, is_active=True).first(),
        'video_lessons': video_lessons,
    }
    return render(request, 'academy/home.html', context)


def apply_admission(request):
    form = AdmissionApplicationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Arizangiz qabul qilindi. Tez orada operatorimiz bog‘lanadi.')
        return redirect('home')
    return render(request, 'academy/application_form.html', {'form': form})


def face_login(request):
    return render(request, 'academy/face_login.html')


def face_login_verify(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Faqat POST so‘rov qabul qilinadi.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        username = payload.get('username', '').strip()
        image = payload.get('image', '')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'message': 'Ma’lumot noto‘g‘ri yuborildi.'}, status=400)

    user = User.objects.filter(username__iexact=username, is_active=True).first()
    if not user:
        return JsonResponse({'ok': False, 'message': 'Bunday foydalanuvchi topilmadi.'}, status=404)
    if not user.photo:
        return JsonResponse({'ok': False, 'message': 'Bu foydalanuvchida profil rasmi yo‘q.'}, status=400)

    try:
        is_match, message = compare_faces(user.photo, image)
    except Exception:
        return JsonResponse({'ok': False, 'message': 'Rasmni tekshirishda xatolik bo‘ldi.'}, status=400)

    if not is_match:
        return JsonResponse({'ok': False, 'message': f'{message}. Yuz mos kelmadi.'}, status=403)

    request._skip_password_activity = True
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    record_login_activity(request, user, LoginActivity.Method.FACE_ID)
    return JsonResponse({'ok': True, 'message': f'{message}. Kirish tasdiqlandi.', 'redirect_url': '/dashboard/'})


@login_required
def dashboard(request):
    request.session['active_role'] = request.user.role
    user = request.user
    if admin_required(user):
        groups = Group.objects.select_related('course', 'teacher').all()
        assignments = Assignment.objects.select_related('group', 'author').order_by('-created_at')[:8]
        pending_submissions = Submission.objects.filter(Q(text__gt='') | Q(file__gt=''), status=Submission.Status.PENDING, teacher_seen_at__isnull=True)
    elif user.role == User.Role.TEACHER:
        groups = user.teaching_groups.select_related('course', 'teacher').all()
        assignments = Assignment.objects.filter(group__teacher=user).select_related('group', 'author').order_by('-created_at')[:8]
        pending_submissions = Submission.objects.filter(Q(text__gt='') | Q(file__gt=''), assignment__group__teacher=user, status=Submission.Status.PENDING, teacher_seen_at__isnull=True)
    elif user.role == User.Role.ASSISTANT:
        groups = user.assistant_groups.select_related('course', 'teacher').all()
        assignments = Assignment.objects.filter(group__assistants=user).select_related('group', 'author').order_by('-created_at')[:8]
        pending_submissions = Submission.objects.filter(Q(text__gt='') | Q(file__gt=''), assignment__group__assistants=user, status=Submission.Status.PENDING, teacher_seen_at__isnull=True)
    else:
        groups = user.student_groups.select_related('course', 'teacher').all()
        assignments = Assignment.objects.filter(group__students=user).select_related('group', 'author').order_by('-created_at')[:8]
        pending_submissions = Submission.objects.none()

    groups = groups.annotate(
        student_count=Count('students', distinct=True),
        pending_count=Count('assignments__submissions', filter=PENDING_WORK_FILTER, distinct=True),
        latest_submission_at=Max('assignments__submissions__submitted_at', filter=SUBMITTED_WORK_FILTER),
    ).order_by('-pending_count', '-latest_submission_at', 'name')
    accepted_submissions = Submission.objects.filter(student=user, status=Submission.Status.ACCEPTED)
    student_score = accepted_submissions.aggregate(total=Sum('score'))['total'] or 0
    student_coins = accepted_submissions.aggregate(total=Sum('silver_coins'))['total'] or 0
    unread_reviewed_submissions = Submission.objects.filter(
        student=user,
        student_seen_review_at__isnull=True,
    ).exclude(status=Submission.Status.PENDING)

    # role-aware counts: admin sees everything, teachers/assistants/students see only their related counts
    if admin_required(user):
        users_count = User.objects.count()
        courses_count = Course.objects.count()
        teachers_count = User.objects.filter(role=User.Role.TEACHER).count()
        students_count = User.objects.filter(role=User.Role.STUDENT).count()
    elif user.role in {User.Role.TEACHER, User.Role.ASSISTANT}:
        users_count = 1
        courses_count = Course.objects.filter(groups__in=groups).distinct().count()
        teachers_count = User.objects.filter(role__in=[User.Role.TEACHER, User.Role.ASSISTANT]).filter(teaching_groups__in=groups).distinct().count()
        students_count = User.objects.filter(role=User.Role.STUDENT).filter(student_groups__in=groups).distinct().count()
    else:
        # student
        users_count = 1
        courses_count = Course.objects.filter(groups__students=user).distinct().count()
        teachers_count = User.objects.filter(role__in=[User.Role.TEACHER, User.Role.ASSISTANT]).filter(teaching_groups__students=user).distinct().count()
        students_count = 1

    context = {
        'users_count': users_count,
        'courses_count': courses_count,
        'teachers_count': teachers_count,
        'students_count': students_count,
        'groups_count': groups.count(),
        'submissions_count': Submission.objects.filter(Q(text__gt='') | Q(file__gt='')).count() if admin_required(user) else Submission.objects.filter(Q(text__gt='') | Q(file__gt=''), student=user).count(),
        'pending_submissions_count': pending_submissions.count(),
        'pending_submissions': pending_submissions.select_related('assignment__group', 'student').order_by('-submitted_at')[:8],
        'groups': groups,
        'assignments': assignments,
        'salaries': Salary.objects.filter(employee=user).order_by('-month')[:4],
        'student_score': student_score,
        'student_coins': student_coins,
        'student_rank': (student_score // 100) + 1 if user.role == User.Role.STUDENT else None,
        'student_notifications_count': unread_reviewed_submissions.count(),
        'unread_reviewed_submissions': unread_reviewed_submissions.select_related('assignment__group').order_by('-reviewed_at')[:6],
        'reviewed_submissions': Submission.objects.filter(student=user).exclude(status=Submission.Status.PENDING).select_related('assignment__group').order_by('-reviewed_at')[:6],
        'recent_users': User.objects.exclude(last_seen__isnull=True).order_by('-last_seen')[:8] if admin_required(user) else [],
        'login_activities': LoginActivity.objects.select_related('user')[:8] if admin_required(user) else [],
    }
    return render(request, 'academy/dashboard.html', context)


@login_required
def student_dashboard(request):
    if not admin_required(request.user):
        raise PermissionDenied
    students = User.objects.filter(role=User.Role.STUDENT).prefetch_related('student_groups__course').order_by('first_name', 'username')
    return render(request, 'academy/student_dashboard.html', {'students': students})


@login_required
def teacher_dashboard(request):
    if not (admin_required(request.user) or request.user.role in {User.Role.TEACHER, User.Role.ASSISTANT}):
        raise PermissionDenied
    teachers = User.objects.filter(role__in=[User.Role.TEACHER, User.Role.ASSISTANT])
    if not admin_required(request.user):
        teachers = teachers.filter(id=request.user.id)
    teachers = teachers.prefetch_related(
        'teaching_groups__course',
        'assistant_groups__course',
        'salaries',
    ).order_by('role', 'first_name', 'username')
    if admin_required(request.user):
        groups = Group.objects.select_related('course', 'teacher')
    elif request.user.role == User.Role.TEACHER:
        groups = request.user.teaching_groups.select_related('course', 'teacher')
    else:
        groups = request.user.assistant_groups.select_related('course', 'teacher')
    groups = groups.annotate(
        student_count=Count('students', distinct=True),
        pending_count=Count('assignments__submissions', filter=PENDING_WORK_FILTER, distinct=True),
        latest_submission_at=Max('assignments__submissions__submitted_at', filter=SUBMITTED_WORK_FILTER),
    ).order_by('-pending_count', '-latest_submission_at', 'name')
    return render(request, 'academy/teacher_dashboard.html', {'teachers': teachers, 'groups': groups})


@login_required
def course_list(request):
    if not admin_required(request.user):
        raise PermissionDenied
    courses = Course.objects.annotate(
        group_count=Count('groups', distinct=True),
        student_count=Count('groups__students', distinct=True),
    ).order_by('title')
    return render(request, 'academy/course_list.html', {'courses': courses})


@login_required
def course_edit(request, pk):
    if not admin_required(request.user):
        raise PermissionDenied
    course = get_object_or_404(Course, pk=pk)
    return save_form(request, CourseForm, 'Kursni tahrirlash', 'course_list', instance=course)


@login_required
def group_list(request):
    user = request.user
    if admin_required(user):
        groups = Group.objects.select_related('course', 'teacher').all()
    elif user.role == User.Role.TEACHER:
        groups = user.teaching_groups.select_related('course', 'teacher').all()
    elif user.role == User.Role.ASSISTANT:
        groups = user.assistant_groups.select_related('course', 'teacher').all()
    else:
        groups = user.student_groups.select_related('course', 'teacher').all()
    groups = groups.annotate(
        student_count=Count('students', distinct=True),
        pending_count=Count('assignments__submissions', filter=PENDING_WORK_FILTER, distinct=True),
        latest_submission_at=Max('assignments__submissions__submitted_at', filter=SUBMITTED_WORK_FILTER),
    ).order_by('-pending_count', '-latest_submission_at', 'name')
    return render(request, 'academy/group_list.html', {'groups': groups})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group.objects.select_related('course', 'teacher'), pk=pk)
    if request.user.role == User.Role.STUDENT:
        if not group.students.filter(id=request.user.id).exists():
            raise PermissionDenied
    elif not can_manage_group(request.user, group):
        raise PermissionDenied
    assignments = group.assignments.select_related('author').annotate(
        pending_count=Count('submissions', filter=Q(submissions__status=Submission.Status.PENDING) & Q(submissions__teacher_seen_at__isnull=True) & (Q(submissions__text__gt='') | Q(submissions__file__gt='')), distinct=True),
        submitted_count=Count('submissions', filter=Q(submissions__text__gt='') | Q(submissions__file__gt=''), distinct=True),
        latest_submission_at=Max('submissions__submitted_at', filter=Q(submissions__text__gt='') | Q(submissions__file__gt='')),
    ).order_by('-pending_count', '-latest_submission_at', '-created_at')
    return render(request, 'academy/group_detail.html', {'group': group, 'assignments': assignments})


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group.objects.select_related('course', 'teacher'), pk=pk)
    if not can_manage_group(request.user, group):
        raise PermissionDenied
    return save_form(request, GroupForm, 'Guruhni tahrirlash', 'group_list', instance=group)


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
    form = GroupForm(request.POST or None)
    suggested_teachers = []
    recent_teachers = User.objects.filter(role__in=[User.Role.TEACHER, User.Role.ASSISTANT]).order_by('-id')[:6]
    unassigned_students = []
    selected_course = None
    # If course selected via GET param (or later via JS), compute suggestions
    course_pk = request.GET.get('course')
    if course_pk:
        try:
            selected_course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            selected_course = None
    # compute suggested teachers (those with least groups in this course)
    if selected_course:
        teachers = User.objects.filter(role__in=[User.Role.TEACHER, User.Role.ASSISTANT]).annotate(
            course_group_count=Count('teaching_groups', filter=Q(teaching_groups__course=selected_course))
        ).order_by('course_group_count', '-last_seen')
        suggested_teachers = list(teachers[:6])
        # students not in any group for this course
        unassigned_students = User.objects.filter(role=User.Role.STUDENT).exclude(student_groups__course=selected_course).order_by('first_name')[:200]

    if request.method == 'POST' and form.is_valid():
        group = form.save()
        messages.success(request, 'Guruh yaratildi.')
        return redirect('dashboard')

    return render(request, 'academy/form.html', {
        'form': form,
        'title': 'Guruh ochish',
        'suggested_teachers': suggested_teachers,
        'recent_teachers': recent_teachers,
        'unassigned_students': unassigned_students,
        'selected_course': selected_course,
    })


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
    return render(request, 'academy/assignment_form.html', {'form': form, 'title': 'Vazifa / imtihon berish'})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('group', 'author'), pk=pk)
    is_student = request.user.role == User.Role.STUDENT
    if is_student and not assignment.group.students.filter(id=request.user.id).exists():
        raise PermissionDenied
    if not is_student and not can_manage_group(request.user, assignment.group):
        raise PermissionDenied

    submission_form = None
    submission = None
    if is_student:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        # Allow submission only if there is no previous submission or the previous one was explicitly rejected
        allow_submit = submission is None or submission.status == Submission.Status.REJECTED
        if allow_submit:
            submission_form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission)
            if request.method == 'POST' and submission_form.is_valid():
                submission = submission_form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.status = Submission.Status.PENDING
                submission.score = None
                submission.silver_coins = 0
                submission.feedback = ''
                submission.reviewed_by = None
                submission.reviewed_at = None
                submission.teacher_seen_at = None
                submission.student_seen_review_at = None
                submission.submitted_at = timezone.now()
                submission.save()
                messages.success(request, 'Ishingiz tizimga yuklandi.')
                return redirect('assignment_detail', pk=assignment.pk)
        else:
            # If a student tries to POST while not allowed, ignore and show message
            if request.method == 'POST':
                messages.error(request, 'Sizda qayta topshirish huquqi yo‘q. Oqituvchi ruxsat berganida qayta topshira olasiz.')
                return redirect('assignment_detail', pk=assignment.pk)

        if submission and submission.status != Submission.Status.PENDING and not submission.student_seen_review_at:
            submission.student_seen_review_at = timezone.now()
            submission.save(update_fields=['student_seen_review_at'])

    submissions = assignment.submissions.select_related('student').filter(Q(text__gt='') | Q(file__gt='')).annotate(
        late_order=Case(
            When(submitted_at__gt=assignment.deadline, then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('late_order', '-submitted_at')
    if not is_student:
        submissions.filter(status=Submission.Status.PENDING, teacher_seen_at__isnull=True).update(teacher_seen_at=timezone.now())
    return render(request, 'academy/assignment_detail.html', {
        'assignment': assignment,
        'submission_form': submission_form,
        'submission': submission,
        'submissions': submissions,
    })


@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission.objects.select_related('assignment__group'), pk=pk)
    if not can_manage_group(request.user, submission.assignment.group):
        raise PermissionDenied
    form = GradeForm(request.POST or None, instance=submission)
    if request.method == 'POST':
        action_status = request.POST.get('status_action')
        if action_status in {Submission.Status.ACCEPTED, Submission.Status.REJECTED}:
            submission.status = action_status
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.student_seen_review_at = None
            submission.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'student_seen_review_at'])
            messages.success(request, f'Ish holati: {submission.get_status_display()}.')
            return redirect('assignment_detail', pk=submission.assignment_id)
        if form.is_valid():
            reviewed_submission = form.save(commit=False)
            if reviewed_submission.status != Submission.Status.PENDING:
                reviewed_submission.reviewed_by = request.user
                reviewed_submission.reviewed_at = timezone.now()
                reviewed_submission.student_seen_review_at = None
            reviewed_submission.save()
            messages.success(request, 'Baho, tanga va izoh saqlandi.')
            return redirect('assignment_detail', pk=submission.assignment_id)
    return render(request, 'academy/form.html', {'form': form, 'title': 'Ishni baholash'})


@login_required
def student_statistics(request):
    if request.user.role != User.Role.STUDENT:
        raise PermissionDenied
    submissions = Submission.objects.filter(student=request.user).select_related('assignment__group').order_by('-submitted_at')
    submissions.filter(student_seen_review_at__isnull=True).exclude(status=Submission.Status.PENDING).update(student_seen_review_at=timezone.now())
    accepted = submissions.filter(status=Submission.Status.ACCEPTED)
    score = accepted.aggregate(total=Sum('score'))['total'] or 0
    coins = accepted.aggregate(total=Sum('silver_coins'))['total'] or 0
    context = {
        'submissions': submissions,
        'score': score,
        'coins': coins,
        'rank': (score // 100) + 1,
        'accepted_count': accepted.count(),
        'rejected_count': submissions.filter(status=Submission.Status.REJECTED).count(),
        'pending_count': submissions.filter(status=Submission.Status.PENDING).filter(Q(text__gt='') | Q(file__gt='')).count(),
    }
    return render(request, 'academy/student_statistics.html', context)


@login_required
def salary_create(request):
    if not admin_required(request.user):
        raise PermissionDenied
    return save_form(request, SalaryForm, 'Oylik chiqarish', 'dashboard')


def save_form(request, form_class, title, redirect_to, instance=None):
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ma’lumot saqlandi.')
        return redirect(redirect_to)
    return render(request, 'academy/form.html', {'form': form, 'title': title})
