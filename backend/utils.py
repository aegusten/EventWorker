from django.contrib.contenttypes.models import ContentType
from backend.models import Message

def get_chat_contacts_for_user(user):
    user_ct = ContentType.objects.get_for_model(user)

    sent = Message.objects.filter(
        sender_content_type=user_ct,
        sender_object_id=user.id
    )

    received = Message.objects.filter(
        receiver_content_type=user_ct,
        receiver_object_id=user.id
    )

    all_msgs = sent.union(received).order_by('-timestamp')

    contact_map = {}
    for msg in all_msgs:
        other = msg.receiver if msg.sender == user else msg.sender
        if not other:
            continue
        key = f"{ContentType.objects.get_for_model(other).pk}-{other.pk}"
        if key not in contact_map:
            contact_map[key] = {
                'user': other,
                'last_message': msg,
            }

    return list(contact_map.values())
