from django.urls import path
from .views import home
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('clock/', TemplateView.as_view(template_name="clock.html")),
]