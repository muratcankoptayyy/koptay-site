#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Blueprint Helpers
Helper functions for API routes including push notifications and device management
"""

import logging
from datetime import datetime, timezone
from models import db, DeviceToken

logger = logging.getLogger(__name__)


def send_push_notification(user_id, title, body, data=None):
    """
    Send push notification to user's devices via Firebase Cloud Messaging
    
    Args:
        user_id: Target user ID
        title: Notification title
        body: Notification body text
        data: Optional dict of additional data
        
    Returns:
        bool: True if notification sent successfully
    """
    try:
        from firebase_notification_service import FirebaseNotificationService
        
        # Get user's device tokens
        tokens = DeviceToken.query.filter_by(user_id=user_id).all()
        
        if not tokens:
            logger.info(f"ℹ No device tokens found for user {user_id}")
            return False

        logger.info(f"📱 Sending push notification to user {user_id}:")
        logger.info(f"   Title: {title}")
        logger.info(f"   Body: {body}")
        logger.info(f"   Data: {data}")
        logger.info(f"   Devices: {len(tokens)}")

        # Get list of FCM tokens
        fcm_tokens = [token.token for token in tokens if token.platform == 'android']
        
        if not fcm_tokens:
            logger.warning(f"⚠ No Android FCM tokens found for user {user_id}")
            return False
        
        # Send via Firebase Cloud Messaging
        notification_service = FirebaseNotificationService()
        results = notification_service.send_notification(
            tokens=fcm_tokens,
            title=title,
            body=body,
            data=data or {}
        )
        
        # Update last_used time for successful tokens
        if results and 'success_count' in results:
            for token in tokens:
                token.last_used = datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"✅ Push notification sent successfully: {results['success_count']}/{len(fcm_tokens)}")
            return True
        else:
            logger.error(f"❌ Push notification failed: {results}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending push notification: {e}")
        import traceback
        traceback.print_exc()
        return False


def clean_expired_tokens(days=90):
    """
    Clean up device tokens that haven't been used in the specified number of days
    
    Args:
        days: Number of days of inactivity before token is considered expired
        
    Returns:
        int: Number of tokens deleted
    """
    try:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        expired_tokens = DeviceToken.query.filter(
            DeviceToken.last_used < cutoff
        ).all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            db.session.delete(token)
        
        db.session.commit()
        logger.info(f"🧹 Cleaned {count} expired device tokens (older than {days} days)")
        return count
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error cleaning expired tokens: {e}")
        return 0
