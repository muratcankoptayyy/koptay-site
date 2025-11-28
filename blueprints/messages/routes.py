"""
Messages Routes
Handles messaging and conversations
"""
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime
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
    
    # Mark messages as read - Update conversation unread count
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
    
    if not content:
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
        message=content
    )
    
    db.session.add(message)
    
    # Update conversation timestamp
    from datetime import timezone
    conversation.updated_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.message,
                'created_at': message.created_at.isoformat(),
                'sender_name': current_user.full_name
            }
        })
    
    return redirect(url_for('messages.conversation', conversation_id=conversation_id))

@messages_bp.route('/start/<int:user_id>')
@login_required
def start_conversation(user_id):
    """Start a new conversation with a user"""
    if user_id == current_user.id:
        flash('Kendinizle mesajlaşamazsınız.', 'warning')
        return redirect(url_for('dashboard'))
    
    other_user = User.query.get_or_404(user_id)
    
    # Check if conversation already exists
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
        ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    if conversation:
        return redirect(url_for('messages.conversation', conversation_id=conversation.id))
    
    # Create new conversation
    conversation = Conversation(
        user1_id=current_user.id,
        user2_id=user_id
    )
    
    db.session.add(conversation)
    db.session.commit()
    
    return redirect(url_for('messages.conversation', conversation_id=conversation.id))
