"""
Chat Blueprint Routes - Mesajlaşma sistemi
"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from sqlalchemy import or_

from blueprints.chat import chat_bp
from blueprints.chat.helpers import (
    _thread_summary, _thread_detail, _create_chat_message, ChatMessageError
)
from models import db, User, Conversation, Message
from utils.logger import get_logger

logger = get_logger(__name__)


@chat_bp.route('/')
@login_required
def chat_index():
    """Phoenix tabanlı mesajlaşma merkezi"""
    user_convs = db.session.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id,
        )
    ).order_by(Conversation.last_message_at.desc()).all()

    active_conversation = user_convs[0] if user_convs else None
    if active_conversation:
        active_conversation.mark_as_read(current_user.id)
        Message.query.filter(
            Message.conversation_id == active_conversation.id,
            Message.sender_id != current_user.id,
            Message.read_at.is_(None),
        ).update({'read_at': datetime.now(timezone.utc)})
        db.session.commit()

    total_unread = sum(conv.get_unread_count(current_user.id) for conv in user_convs)
    active_id = active_conversation.id if active_conversation else None
    threads = [
        _thread_summary(conv, current_user.id, active_id=active_id)
        for conv in user_convs
    ]
    active_thread = _thread_detail(active_conversation, current_user.id) if active_conversation else None
    
    messages = []
    if active_conversation:
        messages = Message.query.filter_by(conversation_id=active_conversation.id).order_by(Message.created_at.asc()).all()

    return render_template('phoenix/messages/inbox.html',
                         threads=threads,
                         active_thread=active_thread,
                         total_unread=total_unread,
                         conversations=user_convs,
                         active_conversation=active_conversation,
                         messages=messages)


@chat_bp.route('/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def conversation(conversation_id):
    """Conversation view with message sending"""
    conversation = Conversation.query.get_or_404(conversation_id)

    if current_user.id not in (conversation.user1_id, conversation.user2_id):
        flash('Bu sohbete erişim yetkiniz yok', 'error')
        return redirect(url_for('chat.chat_index'))

    if request.method == 'POST':
        message_text = request.form.get('message', '')
        reply_to_raw = request.form.get('reply_to_id')
        try:
            reply_to_id = int(reply_to_raw) if reply_to_raw else None
        except (TypeError, ValueError):
            reply_to_id = None

        try:
            _create_chat_message(
                conversation=conversation,
                sender=current_user,
                message_text=message_text,
                reply_to_id=reply_to_id,
                uploaded_file=request.files.get('file'),
            )
            flash('Mesaj gönderildi.', 'success')
        except ChatMessageError as exc:
            flash(str(exc), 'error')
            if exc.status_code == 403:
                return redirect(url_for('chat.chat_index'))
        return redirect(url_for('chat.conversation', conversation_id=conversation_id))

    # Mark as read
    conversation.mark_as_read(current_user.id)
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != current_user.id,
        Message.read_at.is_(None),
    ).update({'read_at': datetime.now(timezone.utc)})
    db.session.commit()

    user_convs = db.session.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id,
        )
    ).order_by(Conversation.last_message_at.desc()).all()

    total_unread = sum(conv.get_unread_count(current_user.id) for conv in user_convs)
    threads = [
        _thread_summary(conv, current_user.id, active_id=conversation.id)
        for conv in user_convs
    ]
    active_thread = _thread_detail(conversation, current_user.id)
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.asc()).all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == '1':
        panel_html = render_template('partials/chat_panel.html',
                                    active_thread=active_thread,
                                    current_user=current_user)
        return jsonify({
            'success': True,
            'panel_html': panel_html,
            'conversation_id': conversation.id,
            'url': url_for('chat.conversation', conversation_id=conversation.id),
        })

    return render_template('phoenix/messages/inbox.html',
                         threads=threads,
                         active_thread=active_thread,
                         total_unread=total_unread,
                         conversations=user_convs,
                         active_conversation=conversation,
                         messages=messages)


@chat_bp.route('/start/<int:user_id>', methods=['GET'])
@login_required
def start_conversation(user_id):
    """Yeni chat başlat veya mevcut olanı aç"""
    if user_id == current_user.id:
        flash('Kendinize mesaj gönderemezsiniz', 'error')
        return redirect(url_for('chat.chat_index'))

    User.query.get_or_404(user_id)
    post_id = request.args.get('post_id', type=int)
    conversation = Conversation.get_or_create(current_user.id, user_id, post_id)
    db.session.commit()

    return redirect(url_for('chat.conversation', conversation_id=conversation.id))


@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Chat mesajı gönder (AJAX) - Dosya desteği ile"""
    try:
        if request.is_json:
            data = request.get_json() or {}
            conversation_id = data.get('conversation_id')
            message_text = data.get('message', '')
            reply_to_raw = data.get('reply_to_id')
            uploaded_file = None
        else:
            conversation_id = request.form.get('conversation_id')
            message_text = request.form.get('message', '')
            reply_to_raw = request.form.get('reply_to_id')
            uploaded_file = request.files.get('file')

        conversation_id = int(conversation_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Geçersiz sohbet'}), 400

    reply_to_id = None
    if reply_to_raw:
        try:
            reply_to_id = int(reply_to_raw)
        except (TypeError, ValueError):
            reply_to_id = None

    conversation = Conversation.query.get_or_404(conversation_id)

    try:
        result = _create_chat_message(
            conversation=conversation,
            sender=current_user,
            message_text=message_text,
            reply_to_id=reply_to_id,
            uploaded_file=uploaded_file,
        )
    except ChatMessageError as exc:
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500

    payload = result['payload']
    return jsonify({'success': True, **payload})


@chat_bp.route('/messages/<int:conversation_id>/new', methods=['GET'])
@login_required
def get_new_messages(conversation_id):
    """Yeni mesajları al (polling için)"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    if current_user.id not in [conversation.user1_id, conversation.user2_id]:
        return jsonify({'success': False, 'error': 'Yetkiniz yok'}), 403
    
    since_id = request.args.get('since_id', type=int, default=0)
    
    new_messages = Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.id > since_id
    ).order_by(Message.created_at.asc()).all()
    
    # Mark as read
    for msg in new_messages:
        if msg.sender_id != current_user.id and not msg.read_at:
            msg.read_at = datetime.now(timezone.utc)
    
    conversation.mark_as_read(current_user.id)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'messages': [{
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.masked_full_name,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_mine': msg.sender_id == current_user.id,
            'read_at': msg.read_at.strftime('%H:%M') if msg.read_at else None
        } for msg in new_messages]
    })


@chat_bp.route('/typing', methods=['POST'])
@login_required
def typing_indicator():
    """Typing indicator (placeholder for WebSocket)"""
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    
    return jsonify({'success': True})


@chat_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Dosya yükle ve mesaj olarak gönder"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['file']
        conversation_id = request.form.get('conversation_id')
        message_text = request.form.get('message', '')
        
        if not conversation_id:
            return jsonify({'success': False, 'error': 'Conversation ID eksik'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
        
        conversation = Conversation.query.get_or_404(conversation_id)
        if current_user.id not in [conversation.user1_id, conversation.user2_id]:
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        result = _create_chat_message(
            conversation=conversation,
            sender=current_user,
            message_text=message_text,
            uploaded_file=file,
        )
        
        return jsonify({'success': True, **result['payload']})
        
    except ChatMessageError as exc:
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except Exception as exc:
        db.session.rollback()
        logger.error(f"File upload error: {exc}")
        return jsonify({'success': False, 'error': str(exc)}), 500
