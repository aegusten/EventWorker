from django.contrib import admin
from django.urls import path, include
from accounts.views import signup_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', signup_view, name='login'),  # default landing page
    path('account/', include('accounts.urls')),
]
