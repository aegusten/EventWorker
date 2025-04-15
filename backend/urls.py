from django.contrib import admin
from django.urls import path
from .views import (
    post_new_job, 
    view_applicants, 
    shortlist_job, 
    message_applicants, 
    delete_job,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('new/', post_new_job, name='org_post_new'),
    path('<int:job_id>/applicants/', view_applicants, name='view_applicants'),
    path('<int:job_id>/shortlist/', shortlist_job, name='shortlist_job'),
    path('<int:job_id>/message/', message_applicants, name='message_applicants'),
    path('<int:job_id>/delete/', delete_job, name='delete_job'),
]
