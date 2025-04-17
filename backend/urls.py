from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.organization_dashboard, name='organization_dashboard'),
    path('profile/', views.organization_profile_view, name='organization_profile_view'),
    path('job/<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('job/<int:job_id>/shortlist/', views.shortlist_job, name='shortlist_job'),
    path('job/<int:job_id>/message/', views.message_applicants, name='message_applicants'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('chat/', views.chat_view, name='chat_view'),
    path('api/job-types/', views.get_allowed_job_types, name='get_allowed_job_types'),
]
