from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def custom_login_redirect(request):
    return redirect("http://user_management:8000/login")
@csrf_exempt
def custom_logout_redirect(request):
    return redirect("http://user_management:8000/logout")

urlpatterns = [
    # login-section
    path("auth/login/", custom_login_redirect, name="login-user"),
    path("auth/logout/", custom_logout_redirect, name="logout-user"),
]