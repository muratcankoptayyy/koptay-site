from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from models import db, Notification, Message, User
from . import main_bp

@main_bp.route('/notifications/check')
@login_required
def check_notifications():
    """Check for new notifications and messages"""
    last_check_str = request.args.get('last_check')
    
    # If last_check is provided and not "null", use it.
    # Otherwise, default to 60 seconds ago to catch anything during page load/refresh.
    if last_check_str and last_check_str != 'null' and last_check_str != '':
        try:
            last_check = datetime.fromisoformat(last_check_str.replace('Z', '+00:00'))
            
            # Safety cap: Don't look back more than 5 minutes to prevent flooding old notifications
            # if the client's stored timestamp is very old
            five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
            if last_check < five_mins_ago:
                last_check = five_mins_ago
                
        except ValueError:
            last_check = datetime.now(timezone.utc) - timedelta(seconds=60)
    else:
        # Initial load or invalid timestamp: look back 60 seconds
        last_check = datetime.now(timezone.utc) - timedelta(seconds=60)
        
    # Get new system notifications
    new_notifications = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.created_at > last_check,
        Notification.read_at.is_(None)
    ).all()
    
    # Get new messages
    # We only want messages from others
    new_messages = Message.query.filter(
        Message.created_at > last_check,
        Message.sender_id != current_user.id,
        Message.read_at.is_(None)
    ).join(User, Message.sender_id == User.id).add_columns(User.full_name, User.avatar_url).all()
    
    # Filter out messages if we are currently in that conversation (handled by frontend usually, but good to have info)
    # For now, we send all, frontend can decide to show or not based on current URL
    
    notifications_data = []
    
    # Process system notifications
    for n in new_notifications:
        notifications_data.append({
            'id': f'notif-{n.id}',
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'url': n.action_url,
            'created_at': n.created_at.isoformat(),
            'icon': 'bell' # Default icon
        })
        
    # Process messages
    for msg, sender_name, sender_avatar in new_messages:
        # Check if this message is for the current user (via conversation)
        # The query already filters by sender_id != current_user.id
        # But we need to make sure the message belongs to a conversation the current user is part of
        # The Message model has conversation_id. We assume the user is part of it if they received it.
        # But strictly speaking, we should join Conversation to be sure, but Message doesn't have direct receiver_id.
        # It relies on Conversation.
        
        # Let's verify the user is part of the conversation
        conversation = msg.conversation
        if conversation and (conversation.user1_id == current_user.id or conversation.user2_id == current_user.id):
            notifications_data.append({
                'id': f'msg-{msg.id}',
                'type': 'message',
                'title': sender_name,
                'message': msg.message if msg.message_type == 'text' else f'[{msg.message_type}]',
                'url': f'/messages/{msg.conversation_id}',
                'created_at': msg.created_at.isoformat(),
                'icon': 'message',
                'avatar': sender_avatar
            })

    return jsonify({
        'notifications': notifications_data,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@main_bp.route('/kullanim-kosullari')
def terms():
    return render_template('pages/legal/terms.html')

@main_bp.route('/gizlilik-politikasi')
def privacy():
    return render_template('pages/legal/privacy.html')

@main_bp.route('/kvkk')
def kvkk():
    return render_template('pages/legal/kvkk.html')

@main_bp.route('/cerez-politikasi')
def cookie_policy():
    from datetime import datetime
    return render_template('pages/legal/cookie_policy.html', now=datetime.now())
