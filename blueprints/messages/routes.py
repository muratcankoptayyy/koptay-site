"""
Messages Routes
Handles messaging and conversations
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from . import messages_bp
from models import db, Conversation, Message, User

@messages_bp.route('/')
@login_required
def list():
    """List all conversations"""
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc()).all()
    
    return render_template('pages/messages/list.html', conversations=conversations)

@messages_bp.route('/<int:conversation_id>')
@login_required
def conversation(conversation_id):
    """View a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check if user is part of the conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        abort(403)
    
    # Get messages
    messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(conversation_id=conversation_id)\
        .filter(Message.sender_id != current_user.id)\
        .filter(Message.read_at == None).all()
    
    if unread_messages:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        for msg in unread_messages:
            msg.read_at = now
            
        # Update conversation unread counts
        if conversation.user1_id == current_user.id:
            conversation.unread_count_user1 = 0
        else:
            conversation.unread_count_user2 = 0
            
        db.session.commit()
    
    # Get other user
    other_user = conversation.user2 if conversation.user1_id == current_user.id else conversation.user1
    
    return render_template('pages/messages/conversation.html', 
                         conversation=conversation, 
                         messages=messages,
                         other_user=other_user)

@messages_bp.route('/<int:conversation_id>/send', methods=['POST'])
@login_required
def send(conversation_id):
    """Send a message in a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check if user is part of the conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        abort(403)
    
    content = request.form.get('content', '').strip()
    message_type = request.form.get('message_type', 'text')
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)
    duration = request.form.get('duration', type=int)
    
    file = request.files.get('file')
    file_url = None
    file_name = None
    file_mime_type = None

    if file and file.filename:
        filename = secure_filename(file.filename)
        # Create directory if not exists
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'messages')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        file_url = f"/static/uploads/messages/{unique_filename}"
        file_name = filename
        file_mime_type = file.content_type

        # Auto-detect type if generic
        if message_type == 'text':
            if file.content_type.startswith('image/'):
                message_type = 'image'
            elif file.content_type.startswith('audio/'):
                message_type = 'audio'
            else:
                message_type = 'file'

    if not content and message_type == 'text' and not file:
        flash('Mesaj boş olamaz.', 'warning')
        return redirect(url_for('messages.conversation', conversation_id=conversation_id))
    
    # Determine receiver and update unread count
    if conversation.user1_id == current_user.id:
        conversation.unread_count_user2 += 1
    else:
        conversation.unread_count_user1 += 1
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        message=content,
        message_type=message_type,
        latitude=latitude,
        longitude=longitude,
        duration=duration,
        file_url=file_url,
        file_name=file_name,
        file_type=file_mime_type
    )
    
    db.session.add(message)
    
    # Update conversation timestamp and last message info
    from datetime import timezone
    now = datetime.now(timezone.utc)
    conversation.updated_at = now
    conversation.last_message_at = now
    conversation.last_message_text = content if message_type == 'text' else f"[{message_type}]"
    conversation.last_message_sender_id = current_user.id
    
    db.session.commit()
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.message,
                'type': message.message_type,
                'file_url': message.file_url,
                'file_name': message.file_name,
                'latitude': message.latitude,
                'longitude': message.longitude,
                'created_at': message.created_at.isoformat(),
                'sender_name': current_user.full_name
            }
        })
    
    return redirect(url_for('messages.conversation', conversation_id=conversation_id))

@messages_bp.route('/<int:conversation_id>/messages')
@login_required
def get_messages(conversation_id):
    """Get messages for a conversation (AJAX)"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check if user is part of the conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        abort(403)
        
    last_id = request.args.get('last_id', type=int)
    
    query = Message.query.filter_by(conversation_id=conversation_id)
    if last_id:
        query = query.filter(Message.id > last_id)
        
    messages = query.order_by(Message.created_at.asc()).all()
    
    # Mark as read if there are new messages from other user
    if messages:
        other_user_id = conversation.user2_id if conversation.user1_id == current_user.id else conversation.user1_id
        unread_msgs = [m for m in messages if m.sender_id == other_user_id and m.read_at is None]
        
        if unread_msgs:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            for m in unread_msgs:
                m.read_at = now
                
            if conversation.user1_id == current_user.id:
                conversation.unread_count_user1 = 0
            else:
                conversation.unread_count_user2 = 0
            db.session.commit()
    
    # Get IDs of recent messages sent by me that are read
    # We check the last 50 messages to keep it efficient
    recent_messages = Message.query.filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    read_message_ids = [m.id for m in recent_messages if m.sender_id == current_user.id and m.read_at is not None]

    return jsonify({
        'messages': [{
            'id': m.id,
            'content': m.message,
            'type': m.message_type,
            'file_url': m.file_url,
            'file_name': m.file_name,
            'latitude': m.latitude,
            'longitude': m.longitude,
            'created_at': m.created_at.strftime('%H:%M'),
            'sender_id': m.sender_id,
            'is_me': m.sender_id == current_user.id,
            'is_read': m.read_at is not None
        } for m in messages],
        'read_message_ids': read_message_ids
    })

@messages_bp.route('/start/<int:user_id>')
@login_required
def start_conversation(user_id):
    """Start a new conversation with a user"""
    print(f"DEBUG: start_conversation called with user_id={user_id}")
    if user_id == current_user.id:
        flash('Kendinizle mesajlaşamazsınız.', 'warning')
        return redirect(url_for('dashboard'))
    
    other_user = User.query.get(user_id)
    if not other_user:
        print(f"ERROR: User {user_id} not found!")
        flash('Kullanıcı bulunamadı.', 'danger')
        return redirect(url_for('dashboard'))
    
    print(f"DEBUG: Found user {other_user.email}")
    
    # Get context from query params
    post_type = request.args.get('post_type')
    post_id = request.args.get('post_id', type=int)
    
    tevkil_post_id = None
    job_post_id = None
    office_post_id = None
    
    if post_type == 'tevkil' and post_id:
        tevkil_post_id = post_id
    elif post_type == 'job' and post_id:
        job_post_id = post_id
    elif post_type == 'office' and post_id:
        office_post_id = post_id
    
    # Create or get conversation with context
    conversation = Conversation.get_or_create(
        user1_id=current_user.id,
        user2_id=user_id,
        post_id=tevkil_post_id,
        job_post_id=job_post_id,
        office_post_id=office_post_id
    )
    
    # Commit to ensure ID is persisted before redirect
    db.session.commit()
    
    return redirect(url_for('messages.conversation', conversation_id=conversation.id))
