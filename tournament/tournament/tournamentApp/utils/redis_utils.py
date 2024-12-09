import redis
import json
import logging

logger = logging.getLogger(__name__)


redis_client = redis.StrictRedis(host='redis', port=6379, db=1)

def create_channel_and_invite_users(channel_name, user_id, all_users):
    """
    Create a new Redis channel and send notifications to all users.
    """
    channel_key = f"channel:{channel_name}"
    redis_client.sadd(channel_key, user_id)  # Add the creator to the channel

    # Notify all users about the new channel invite
    notification = {
        "type": "chat",
        "message": "You have been invited to a new channel",
        # "action": "invite",
        # "channel": channel_name,
        # "inviter": user_id,
    }
    for user in all_users:
        user_channel = "global_chat"
        redis_client.publish(user_channel, json.dumps(notification))