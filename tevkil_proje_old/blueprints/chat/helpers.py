"""
Chat Blueprint Helpers - Thread summaries, message creation, formatting
"""
from datetime import datetime, timezone
from flask import url_for
from models import db, Message
from utils.logger import get_logger
import os

logger = get_logger(__name__)


def _user_initials(user):
    """Get user initials from name"""
    if not user:
        return "?"
    
    full_name = user.masked_full_name if hasattr(user, "masked_full_name") else user.full_name
    if not full_name:
        return "?"
    
    parts = full_name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][0].upper()
    return "?"


def _normalise_to_utc(dt):
    """Normalize datetime to UTC"""
    if not dt:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _format_relative_time(dt):
    """Format datetime as relative time"""
    if not dt:
        return ""
    
    dt = _normalise_to_utc(dt)
    now = datetime.now(timezone.utc)
    delta = now - dt
    
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "az önce"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} dk"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} sa"
    days = hours // 24
    if days < 7:
        return f"{days} gün"
    weeks = days // 7
    if weeks < 4:
        return f"{weeks} hf"
    return dt.strftime('%d.%m.%Y')


def _format_file_size(size_bytes):
    """Format file size in human readable format"""
    if not size_bytes:
        return None
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def _conversation_meta(conversation):
    """Get conversation metadata"""
    meta = []
    if conversation.post_id and conversation.post:
        meta.append(f"İlan: {conversation.post.title[:30]}...")
    return " • ".join(meta) if meta else None


def _thread_summary(conversation, current_user_id, active_id):
    """Convert conversation into sidebar summary"""
    other_user = conversation.get_other_user(current_user_id)
    return {
        "id": conversation.id,
        "name": other_user.masked_full_name if hasattr(other_user, "masked_full_name") else other_user.full_name,
        "initials": _user_initials(other_user),
        "last_timestamp": _format_relative_time(conversation.last_message_at or conversation.updated_at),
        "preview": conversation.last_message_text or "Henüz mesaj yok",
        "unread": conversation.get_unread_count(current_user_id),
        "active": active_id == conversation.id,
        "meta": _conversation_meta(conversation),
        "url": url_for("chat.conversation", conversation_id=conversation.id),
    }


def _thread_detail(conversation, current_user_id):
    """Build the active chat panel payload"""
    logger.debug(f"conversation: {conversation}, user_id: {current_user_id}")
    other_user = conversation.get_other_user(current_user_id)
    logger.debug(f"other_user: {other_user}")
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.asc()).all()
    logger.debug(f"messages count: {len(messages)}")
    
    result = {
        "id": conversation.id,
        "name": other_user.masked_full_name if hasattr(other_user, "masked_full_name") else other_user.full_name,
        "initials": _user_initials(other_user),
        "meta": _conversation_meta(conversation),
        "post": {
            "title": conversation.post.title,
            "url": url_for("posts.post_detail", post_id=conversation.post_id),
        } if conversation.post_id else None,
        "other_user_id": other_user.id,
        "messages": [
            {
                "id": msg.id,
                "body": msg.message,
                "message": msg.message,
                "timestamp": _normalise_to_utc(msg.created_at).strftime('%d.%m.%Y %H:%M') if msg.created_at else "",
                "is_owner": msg.sender_id == current_user_id,
                "type": msg.message_type or "text",
                "file_url": msg.file_url,
                "file_name": msg.file_name,
                "file_size": _format_file_size(msg.file_size),
            }
            for msg in messages
        ],
    }
    logger.debug(f"result keys: {result.keys()}, messages in result: {len(result['messages'])}")
    return result


def _build_message_payload(message, sender, other_user, message_text, message_type,
                           file_url, file_name, file_size, file_type, reply_to_id):
    """Serialize Message for realtime transport"""
    masked_sender_name = sender.masked_full_name if hasattr(sender, "masked_full_name") else sender.full_name
    sender_avatar = (
        sender.avatar_url
        if getattr(sender, "avatar_url", None)
        else f"https://ui-avatars.com/api/?name={masked_sender_name.replace(' ', '+')}&background=1f2937&color=fff"
    )
    created_at = _normalise_to_utc(message.created_at)
    read_at = _normalise_to_utc(message.read_at)

    return {
        'id': message.id,
        'conversation_id': message.conversation_id,
        'sender_id': sender.id,
        'sender_name': masked_sender_name,
        'sender_avatar': sender_avatar,
        'receiver_id': other_user.id if other_user else None,
        'text': message_text,
        'message_type': message_type or 'text',
        'file_url': file_url,
        'file_name': file_name,
        'file_size': file_size,
        'file_type': file_type,
        'reply_to_id': reply_to_id,
        'created_at': created_at.isoformat() if created_at else None,
        'created_at_display': created_at.strftime('%H:%M') if created_at else '',
        'read_at': read_at.isoformat() if read_at else None,
        'read_at_display': read_at.strftime('%H:%M') if read_at else None,
    }


def _serialize_conversation_state(conversation):
    """Expose conversation counters for UI refresh"""
    last_dt = _normalise_to_utc(conversation.last_message_at)
    state = {
        'id': conversation.id,
        'user1_id': conversation.user1_id,
        'user2_id': conversation.user2_id,
        'unread_count_user1': conversation.unread_count_user1,
        'unread_count_user2': conversation.unread_count_user2,
        'last_message_text': conversation.last_message_text,
        'last_message_sender_id': conversation.last_message_sender_id,
        'last_message_at': last_dt.isoformat() if last_dt else None,
        'last_message_at_clock': last_dt.strftime('%H:%M') if last_dt else None,
        'last_message_at_human': _format_relative_time(last_dt) if last_dt else '',
        'meta': _conversation_meta(conversation),
    }
    if conversation.post_id:
        state['post_id'] = conversation.post_id
        state['post_title'] = conversation.post.title if conversation.post else None
    return state


class ChatMessageError(Exception):
    """Chat message creation error"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def _create_chat_message(conversation, sender, message_text="", reply_to_id=None, uploaded_file=None):
    """Create and send a chat message with optional file attachment"""
    from blueprints.helpers import create_notification, sanitize_filename
    import secrets
    from werkzeug.utils import secure_filename
    
    # Validation
    if sender.id not in [conversation.user1_id, conversation.user2_id]:
        raise ChatMessageError("Bu sohbete katılma yetkiniz yok", 403)
    
    if not message_text and not uploaded_file:
        raise ChatMessageError("Mesaj veya dosya göndermelisiniz", 400)
    
    message_text = (message_text or "").strip()[:5000]
    
    # File handling
    file_url = None
    file_name = None
    file_size = None
    file_type = None
    message_type = "text"
    
    if uploaded_file and uploaded_file.filename:
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip'}
        max_file_size = 10 * 1024 * 1024  # 10MB
        
        filename = secure_filename(uploaded_file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise ChatMessageError(f"Desteklenmeyen dosya türü: {file_ext}", 400)
        
        uploaded_file.seek(0, 2)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)
        
        if file_size > max_file_size:
            raise ChatMessageError("Dosya boyutu 10MB'ı aşamaz", 400)
        
        # Save file
        upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'chat')
        os.makedirs(upload_folder, exist_ok=True)
        
        safe_filename = sanitize_filename(filename)
        file_path = os.path.join(upload_folder, safe_filename)
        uploaded_file.save(file_path)
        
        file_url = f"/static/uploads/chat/{safe_filename}"
        file_name = filename
        
        if file_ext in {'.jpg', '.jpeg', '.png', '.gif'}:
            message_type = "image"
            file_type = "image"
        else:
            message_type = "file"
            file_type = "document"
    
    # Create message
    other_user = conversation.get_other_user(sender.id)
    
    message = Message(
        conversation_id=conversation.id,
        sender_id=sender.id,
        message=message_text or f"📎 {file_name}",
        message_type=message_type,
        file_url=file_url,
        file_name=file_name,
        file_size=file_size,
        reply_to_id=reply_to_id,
    )
    db.session.add(message)
    
    # Update conversation
    conversation.last_message_text = message.message
    conversation.last_message_sender_id = sender.id
    conversation.last_message_at = datetime.now(timezone.utc)
    
    if sender.id == conversation.user1_id:
        conversation.unread_count_user2 = (conversation.unread_count_user2 or 0) + 1
    else:
        conversation.unread_count_user1 = (conversation.unread_count_user1 or 0) + 1
    
    db.session.commit()
    
    # Send notification
    create_notification(
        user_id=other_user.id,
        notification_type='new_message',
        title='Yeni Mesaj',
        message=f'{sender.masked_full_name if hasattr(sender, "masked_full_name") else sender.full_name} mesaj gönderdi',
        related_user_id=sender.id,
        action_url=url_for('chat.conversation', conversation_id=conversation.id),
        action_text='Mesajı Gör'
    )
    
    payload = _build_message_payload(
        message, sender, other_user, message_text, message_type,
        file_url, file_name, file_size, file_type, reply_to_id
    )
    
    return {
        'message': message,
        'payload': payload,
        'conversation_state': _serialize_conversation_state(conversation)
    }
