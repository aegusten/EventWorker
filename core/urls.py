from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

from .views import (
    home_redirect_view, 
    login_view, 
    register_view, 
    base_redirect_view,
    logout_view,
    check_uniqueness,
    applicant_dashboard,
    organization_dashboard,
    update_security_questions,
    change_password,
    verify_password,
    get_security_questions,
    public_verify_security_answers,
    get_security_questions_choices,
)

urlpatterns = [
    path('', home_redirect_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('base/', base_redirect_view, name='base'),
    path('logout/', logout_view, name='logout'),
    path('account/check_uniqueness/', check_uniqueness, name='check_uniqueness'),
    path('account/', include('users.urls')),
    path('dashboard/organization/', organization_dashboard, name='organization_dashboard'),
    path('dashboard/applicant/', applicant_dashboard, name='applicant_dashboard'),
    path('jobs/', include('backend.urls')),
    path('organization/', include('backend.urls')),
    path('update_security_questions/', update_security_questions, name='update_security_questions'),
    path('change_password/', change_password, name='change_password'),
    path('verify_password/', verify_password, name='verify_password'),
    path('get_security_questions/', get_security_questions, name='get_security_questions'),
    path('verify_security_answers/', public_verify_security_answers, name='verify_security_answers'),
    path('get_security_questions_choices/', get_security_questions_choices, name='get_security_questions_choices'),
    path('account/', include('users.urls')),
   path('chat/<int:job_id>/<int:target_user_id>/', views.chat_with_user_view, name='chat_with_user'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
