from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
import redis
from django.conf import settings
import json

redis_client = redis.StrictRedis(host='redis', port=6379, db=1)

class ChannelInviteView(APIView):
    # Override the default authentication and permission classes
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Extract the JWT from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            # Decode the JWT (replace 'your_secret_key' with your actual secret key)
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('user_id')
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        channel_name = 'global_chat'
        notification = {
            "type": "chat",
            "message": "ping",
            "group": "global",
            "sender": "tournament_app"
        }
        
        redis_client.publish(channel_name, json.dumps(notification))
        return Response({"message": "Message sent to global chat"}, status=status.HTTP_201_CREATED)