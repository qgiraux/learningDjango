import json
import logging
from django.http import HttpResponse
from .models import Friends
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.http import JsonResponse
import jwt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})


# @api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddFriend(request):
    try:
        # Extract JSON data from request body
        data = json.loads(request.body)
        logger.error(f"Request body: {data}")

        # Extract and decode the JWT token
        auth_header = request.headers.get('Authorization').split()[1]
        decoded = jwt.decode(auth_header, settings.SECRET_KEY, algorithms=["HS256"])
        logger.error(f"Decoded token: {decoded}")

        # Extract user ID from the decoded token
        user_id = decoded.get('user_id')
        if not user_id:
            return HttpResponse(
                json.dumps({'detail': 'User not found', 'code': 'user_not_found'}),
                status=400,
                content_type='application/json'
            )

        # Extract friend ID from the request data
        friend_id = data.get('id')
        if not friend_id:
            return HttpResponse(
                json.dumps({'detail': 'Friend ID is required', 'code': 'friend_id_required'}),
                status=400,
                content_type='application/json'
            )

        # Create a new friend relationship
        new = Friends()
        new.friend_id = friend_id
        new.user_id = user_id
        new.save()

        # Prepare response body
        body = json.dumps({'message': 'Friend added successfully'})
        return HttpResponse(body, status=200, content_type='application/json')

    except jwt.ExpiredSignatureError:
        return HttpResponse(
            json.dumps({'detail': 'Token has expired', 'code': 'token_expired'}),
            status=400,
            content_type='application/json'
        )
    except jwt.InvalidTokenError:
        return HttpResponse(
            json.dumps({'detail': 'Invalid token', 'code': 'invalid_token'}),
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HttpResponse(
            json.dumps({'detail': 'An error occurred', 'code': 'error_occurred'}),
            status=500,
            content_type='application/json'
        )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Friendslist(request):
    logger = logging.getLogger(__name__)
    auth_header = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(auth_header, settings.SECRET_KEY, algorithms=["HS256"])
    # logger.error("test" + decoded)
    logger.error('BEGIN!!!!!!!!')
    logger.error(decoded)
    logger.error('END!!!!!!!!')
    user_id = decoded['user_id']    
    if not user_id:
        return HttpResponse(json.dumps({'detail': 'User ID not found in token', 'code': 'user_id_not_found'}), status=400, content_type='application/json')
    friend_ids = list(Friends.objects.filter(user_id=decoded['user_id']).values_list('friend_id', flat=True))
    if not friend_ids:
        return HttpResponse(json.dumps({'detail': 'no friends found', 'code': 'friends_not_found'}), status=400, content_type='application/json')
    return HttpResponse(json.dumps(friend_ids), status=200, content_type='application/json')

# @csrf_exempt
# @api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def RemoveFriend(request):
    # Extract 'id' from query parameters
    auth_header = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(auth_header, settings.SECRET_KEY, algorithms=["HS256"])
    friend_id = request.query_params.get('id')
    if not friend_id:
        return HttpResponse(json.dumps({'error': 'Friend ID is required'}), status=400, content_type='application/json')
    # Delete the friend relationship
    deleted, _ = Friends.objects.filter(user_id=request.decode['user_id'], friend_id=friend_id).delete()
    if deleted:
        return HttpResponse(json.dumps({'message': 'Friend removed successfully'}), status=200, content_type='application/json')
    else:
        return HttpResponse(json.dumps({'error': 'Friend not found'}), status=404, content_type='application/json')