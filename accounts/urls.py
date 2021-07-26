from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_user, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("validate-username/", views.validate_username, name="validate_username"),
    path("validate-email/", views.validate_email, name="validate_email"),
]
