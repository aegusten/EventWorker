from backend.models import Message
from django.contrib.contenttypes.models import ContentType

def get_user_conversations(user):

    user_ct = ContentType.objects.get_for_model(user.__class__)

    messages = Message.objects.filter(
        Q(sender_content_type=user_ct, sender_object_id=user.id) |
        Q(receiver_content_type=user_ct, receiver_object_id=user.id)
    ).select_related('job')

    # Map the messages to create a conversation
    conversation_map = {}

    for msg in messages:
        # Determine partner based on who sent the message
        if msg.sender == user:
            partner = msg.receiver
        else:
            partner = msg.sender

        key = (partner, msg.job)
        if key not in conversation_map or msg.timestamp > conversation_map[key].timestamp:
            conversation_map[key] = msg

    # Sort conversations by timestamp
    sorted_conversations = sorted(conversation_map.items(), key=lambda x: x[1].timestamp, reverse=True)

    return sorted_conversations
