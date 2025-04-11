from django.urls import path
from . import views
from users.views import register_view 
from .views import get_security_questions

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('ajax/validate-login/', views.validate_login_ajax, name='validate_login_ajax'),
    path('forgot-password/', views.public_verify_security_answers, name='forgot_password_check'), 
    path('reset-password/', views.reset_password, name='reset_password'),
    path('security-questions/', get_security_questions, name='security_questions'),
]
