from django.urls import path, include
from django.conf.urls.static import static
from users.views import home_redirect_view

from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('', home_redirect_view),
    path('admin/', admin.site.urls),
    path('account/', include('users.urls')),
    path('jobs/', include('backend.urls')),
    path('backend/', include('backend.urls')),

]

urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)