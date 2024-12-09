import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from tournamentApp.routing import websocket_urlpatterns  # Import your WebSocket routing configuration

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tournament.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})