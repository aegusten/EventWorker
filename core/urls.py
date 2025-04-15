from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    home_redirect_view, 
    login_view, 
    register_view, 
    base_redirect_view,
    logout_view,
    check_uniqueness,
)

urlpatterns = [
 
    path('', home_redirect_view, name='home'),
    path('admin/', admin.site.urls),

    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('base/', base_redirect_view, name='base'),
    path('logout/', logout_view, name='logout'),
    path('account/check_uniqueness/', check_uniqueness, name='check_uniqueness'),
    path('account/', include('users.urls')),

    path('jobs/', include('backend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
