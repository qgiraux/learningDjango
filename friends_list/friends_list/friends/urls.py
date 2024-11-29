from django.urls import path
from .views import AddFriend , Friendslist, RemoveFriend, get_csrf_token


urlpatterns = [
    path('addfriend/', AddFriend, name='add friend'),
    path('friendslist/', Friendslist, name='friends list'),
    path('removefriend/', RemoveFriend, name='remove friend'),
    path('csrf/', get_csrf_token, name='get csrf'),
]