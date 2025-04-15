from django.urls import path
from . import views

urlpatterns = [
    path('change-password/', views.change_password, name='change-password'),
    path('profile/', views.profile_view, name='profile_view'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/', views.chat_view, name='chat_view'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-security/', views.change_security_phrase, name='change_security_phrase'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('forgot-password-check/', views.change_password, name='forgot_password_check'),
    path('account/verify-password/', views.verify_password, name='verify_password'),
    path('change_password/', views.change_password, name='change_password'),
    path('verify_security_answers/', views.verify_security_answers, name='verify_security_answers'),
]

