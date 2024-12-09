from django.urls import path
from .views import ChannelInviteView

urlpatterns = [
    path('invite/', ChannelInviteView.as_view(), name='channel-invite'),    
]
