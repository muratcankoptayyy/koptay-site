"""
Firebase Cloud Messaging (FCM) Service
Push notification implementation for mobile apps
"""

import os
import json
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, messaging

class FirebaseNotificationService:
    """Handle push notifications via Firebase Cloud Messaging"""
    
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        try:
            # Firebase credentials from environment variable
            firebase_cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
            
            if not firebase_cred_json:
                print("⚠️ FIREBASE_CREDENTIALS_JSON not set - push notifications disabled")
                return
            
            # Parse JSON credentials
            cred_dict = json.loads(firebase_cred_json)
            cred = credentials.Certificate(cred_dict)
            
            # Initialize Firebase Admin
            firebase_admin.initialize_app(cred)
            cls._initialized = True
            print("✅ Firebase Admin SDK initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
    
    @classmethod
    def send_notification(
        cls,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Send push notification to a single device
        
        Args:
            token: FCM device token
            title: Notification title
            body: Notification message
            data: Additional data payload
            image_url: Optional image URL for rich notification
            
        Returns:
            bool: True if sent successfully
        """
        if not cls._initialized:
            cls.initialize()
            if not cls._initialized:
                return False
        
        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # Build Android config for high priority
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#1E3A8A',  # Primary blue color
                    sound='default',
                    channel_id='tevkil_notifications'
                )
            )
            
            # Build message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=token,
                android=android_config
            )
            
            # Send message
            response = messaging.send(message)
            print(f"✅ Notification sent successfully: {response}")
            return True
            
        except messaging.UnregisteredError:
            print(f"⚠️ Token unregistered: {token[:20]}...")
            return False
        except Exception as e:
            print(f"❌ Failed to send notification: {e}")
            return False
    
    @classmethod
    def send_multicast(
        cls,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Send notification to multiple devices
        
        Args:
            tokens: List of FCM device tokens
            title: Notification title
            body: Notification message
            data: Additional data payload
            image_url: Optional image URL
            
        Returns:
            dict: {'success': count, 'failure': count, 'invalid_tokens': [tokens]}
        """
        if not cls._initialized:
            cls.initialize()
            if not cls._initialized:
                return {'success': 0, 'failure': len(tokens), 'invalid_tokens': []}
        
        if not tokens:
            return {'success': 0, 'failure': 0, 'invalid_tokens': []}
        
        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # Build Android config
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#1E3A8A',
                    sound='default',
                    channel_id='tevkil_notifications'
                )
            )
            
            # Build multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=data or {},
                tokens=tokens,
                android=android_config
            )
            
            # Send to multiple devices
            response = messaging.send_multicast(message)
            
            # Collect invalid tokens
            invalid_tokens = []
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        if isinstance(resp.exception, messaging.UnregisteredError):
                            invalid_tokens.append(tokens[idx])
            
            result = {
                'success': response.success_count,
                'failure': response.failure_count,
                'invalid_tokens': invalid_tokens
            }
            
            print(f"📊 Multicast result: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Failed to send multicast: {e}")
            return {
                'success': 0,
                'failure': len(tokens),
                'invalid_tokens': []
            }
    
    @classmethod
    def send_topic_notification(
        cls,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send notification to a topic (group of users)
        
        Args:
            topic: Topic name (e.g., 'new_applications', 'all_lawyers')
            title: Notification title
            body: Notification message
            data: Additional data payload
            
        Returns:
            bool: True if sent successfully
        """
        if not cls._initialized:
            cls.initialize()
            if not cls._initialized:
                return False
        
        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body
            )
            
            # Build Android config
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#1E3A8A',
                    sound='default',
                    channel_id='tevkil_notifications'
                )
            )
            
            # Build message for topic
            message = messaging.Message(
                notification=notification,
                data=data or {},
                topic=topic,
                android=android_config
            )
            
            # Send to topic
            response = messaging.send(message)
            print(f"✅ Topic notification sent: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send topic notification: {e}")
            return False
    
    @classmethod
    def subscribe_to_topic(cls, tokens: List[str], topic: str) -> bool:
        """Subscribe devices to a topic"""
        if not cls._initialized:
            cls.initialize()
            if not cls._initialized:
                return False
        
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            print(f"✅ Subscribed {response.success_count} devices to topic '{topic}'")
            return True
        except Exception as e:
            print(f"❌ Failed to subscribe to topic: {e}")
            return False
    
    @classmethod
    def unsubscribe_from_topic(cls, tokens: List[str], topic: str) -> bool:
        """Unsubscribe devices from a topic"""
        if not cls._initialized:
            cls.initialize()
            if not cls._initialized:
                return False
        
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            print(f"✅ Unsubscribed {response.success_count} devices from topic '{topic}'")
            return True
        except Exception as e:
            print(f"❌ Failed to unsubscribe from topic: {e}")
            return False


# Initialize on import
FirebaseNotificationService.initialize()
