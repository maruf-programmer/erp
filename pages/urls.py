from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.apply_admission, name='apply_admission'),
    path('face-login/', views.face_login, name='face_login'),
    path('api/face-login/', views.face_login_verify, name='face_login_verify'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/students/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teachers/', views.teacher_dashboard, name='teacher_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/new/', views.group_create, name='group_create'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('assignments/new/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('statistics/', views.student_statistics, name='student_statistics'),
    path('salaries/new/', views.salary_create, name='salary_create'),
]
