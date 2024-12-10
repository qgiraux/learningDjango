# your_app/routing.py
from django.urls import path
from .consumers import tournamentConsumer

websocket_urlpatterns = [
    path('ws/tournament/', tournamentConsumer.as_asgi()),
]
