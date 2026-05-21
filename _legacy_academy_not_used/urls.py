from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.apply_admission, name='apply_admission'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('courses/new/', views.course_create, name='course_create'),
    path('groups/new/', views.group_create, name='group_create'),
    path('assignments/new/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('salaries/new/', views.salary_create, name='salary_create'),
]
