from django.urls import path
from . import views
from users.views import register_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path("ajax/validate-login/", views.validate_login_ajax, name="validate_login_ajax"),
    path('register/', register_view, name='register'),

]
