import redis
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def is_user_online(user_id):
    
    channel_layer = get_channel_layer()
    logger.error(channel_layer)
    user_channel_name = f"user_{user_id}"
    # Check if the user is part of the global_chat group
    logger.error("checkpoint")
    print_redis_content
    redis_client = redis.StrictRedis(host='redis', port=6379, db=1)
    user_status = redis_client.hget('global', user_id)
    logger.error("222")
    return user_status is not None



def print_redis_content():
    logger = logging.getLogger(__name__)
    redis_client = redis.StrictRedis(host='redis', port=6379, db=10)
    global_hash = redis_client.hgetall('global')
    for user_id, nickname in global_hash.items():
        logger.error(f"user_id: {user_id.decode('utf-8')}")