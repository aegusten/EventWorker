from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/', views.chat_view, name='chat_view'),
    path('search/', views.search_jobs, name='search_jobs'),
]

