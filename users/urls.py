from django.urls import path
from . import views
from users.views import register_view 
from .views import get_security_questions, get_security_questions_choices

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.public_verify_security_answers, name='forgot_password_check'), 
    path('reset-password/', views.reset_password, name='reset_password'),
    path('security-questions/', get_security_questions, name='security_questions'),
    path('api/get-security-questions-choices/', get_security_questions_choices, name='get_security_questions_choices'),
]
