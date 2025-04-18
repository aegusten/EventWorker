from django.urls import path
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('applicant/catalog/', views.applicant_catalog_view, name='applicant_catalog'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('dashboard/applicant/', views.applicant_dashboard, name='applicant_dashboard'),
    path('recently-applied/', views.recently_applied_view, name='recently_applied'),
    path("feedback/<int:app_id>/submit/", views.submit_feedback, name="submit_feedback"),
    re_path(r'^chat(?:/(?P<job_id>\d+))?/$', views.applicant_chat_view, name='applicant_chat_view'),
    path('download-cv/', views.download_cv, name='download_cv'),
]

