from django.urls import path
from . import views
from .views import get_security_questions, get_security_questions_choices, base_redirect_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.public_verify_security_answers, name='forgot_password_check'), 
    path('reset-password/', views.reset_password, name='reset_password'),
    path('security-questions/', get_security_questions, name='security_questions'),
    path('api/get-security-questions-choices/', get_security_questions_choices, name='get_security_questions_choices'),
    path('check_uniqueness/', views.check_uniqueness, name='check_uniqueness'),
    path('home/', base_redirect_view, name='base'),
    
    path('profile/', views.profile_view, name='profile'),
    path('chat/', views.chat_view, name='chat'),
    path('logout/', views.logout_view, name='logout'), 
    
    path('dashboard/applicant/', views.applicant_dashboard, name='applicant_dashboard'),
    path('dashboard/organization/', views.organization_dashboard, name='org_dashboard'),
    path('dashboard/organization/new/', views.post_new_job, name='org_post_new'),
]