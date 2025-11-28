"""
🔄 Mesajlaşma sistemini chat sistemine dönüştürme migration scripti
"""

from app import app, db
from models import User, Message, Conversation, TevkilPost
from datetime import datetime
from sqlalchemy import text

def migrate_to_chat_system():
    """Eski mesajlaşma sistemini conversation-based chat sistemine dönüştür"""
    
    with app.app_context():
        print("🚀 Chat sistemine migration başlatılıyor...")
        
        # 1. Conversations tablosu oluştur
        print("\n📊 1. Conversations tablosu oluşturuluyor...")
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    post_id INTEGER,
                    last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_message_text TEXT,
                    last_message_sender_id INTEGER,
                    unread_count_user1 INTEGER DEFAULT 0,
                    unread_count_user2 INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user1_id) REFERENCES users(id),
                    FOREIGN KEY (user2_id) REFERENCES users(id),
                    FOREIGN KEY (post_id) REFERENCES tevkil_posts(id),
                    FOREIGN KEY (last_message_sender_id) REFERENCES users(id),
                    UNIQUE (user1_id, user2_id, post_id)
                )
            """))
            db.session.commit()
            print("   ✅ Conversations tablosu oluşturuldu")
        except Exception as e:
            print(f"   ⚠️  Conversations tablosu zaten var veya hata: {e}")
            db.session.rollback()
        
        # 2. Messages tablosuna yeni kolonlar ekle
        print("\n📊 2. Messages tablosuna yeni kolonlar ekleniyor...")
        
        # conversation_id ekle
        try:
            db.session.execute(text("""
                ALTER TABLE messages ADD COLUMN conversation_id INTEGER REFERENCES conversations(id)
            """))
            db.session.commit()
            print("   ✅ conversation_id kolonu eklendi")
        except Exception as e:
            print(f"   ⚠️  conversation_id zaten var veya hata: {e}")
            db.session.rollback()
        
        # reply_to_id ekle
        try:
            db.session.execute(text("""
                ALTER TABLE messages ADD COLUMN reply_to_id INTEGER REFERENCES messages(id)
            """))
            db.session.commit()
            print("   ✅ reply_to_id kolonu eklendi")
        except Exception as e:
            print(f"   ⚠️  reply_to_id zaten var veya hata: {e}")
            db.session.rollback()
        
        # delivered_at ekle (SQLite için default olmadan)
        try:
            db.session.execute(text("""
                ALTER TABLE messages ADD COLUMN delivered_at DATETIME
            """))
            db.session.commit()
            print("   ✅ delivered_at kolonu eklendi")
            
            # Tüm mevcut mesajlar için delivered_at'i created_at ile aynı yap
            db.session.execute(text("""
                UPDATE messages SET delivered_at = created_at WHERE delivered_at IS NULL
            """))
            db.session.commit()
            print("   ✅ Mevcut mesajların delivered_at değerleri güncellendi")
        except Exception as e:
            print(f"   ⚠️  delivered_at zaten var veya hata: {e}")
            db.session.rollback()
        
        # 3. Eski mesajları conversation'lara dönüştür
        print("\n📊 3. Eski mesajlar conversation'lara dönüştürülüyor...")
        
        # Tüm mesajları al
        all_messages = Message.query.order_by(Message.created_at).all()
        
        conversation_map = {}  # (user1_id, user2_id, post_id) -> conversation_id
        migrated_count = 0
        
        for msg in all_messages:
            # Skip if already has conversation_id
            if msg.conversation_id:
                continue
            
            # Kullanıcı ID'lerini sırala (küçük önce)
            user1_id = min(msg.sender_id, msg.receiver_id)
            user2_id = max(msg.sender_id, msg.receiver_id)
            post_id = msg.post_id
            
            # Conversation key
            conv_key = (user1_id, user2_id, post_id)
            
            # Conversation var mı kontrol et
            if conv_key not in conversation_map:
                # Yeni conversation oluştur
                conversation = Conversation(
                    user1_id=user1_id,
                    user2_id=user2_id,
                    post_id=post_id,
                    created_at=msg.created_at,
                    last_message_at=msg.created_at,
                    last_message_text=msg.message[:100] if msg.message else "",
                    last_message_sender_id=msg.sender_id
                )
                db.session.add(conversation)
                db.session.flush()
                
                conversation_map[conv_key] = conversation.id
                print(f"   📝 Conversation {conversation.id} oluşturuldu: User {user1_id} ↔ User {user2_id}")
            
            # Mesajı conversation'a bağla
            msg.conversation_id = conversation_map[conv_key]
            
            # delivered_at'i set et (eski mesajlar iletilmiş sayılır)
            if not msg.delivered_at:
                msg.delivered_at = msg.created_at
            
            migrated_count += 1
        
        # Commit all changes
        db.session.commit()
        
        # 4. Conversation'ların son mesaj bilgilerini güncelle
        print("\n📊 4. Conversation son mesaj bilgileri güncelleniyor...")
        
        for conversation in Conversation.query.all():
            # Son mesajı bul
            last_msg = Message.query.filter_by(
                conversation_id=conversation.id
            ).order_by(Message.created_at.desc()).first()
            
            if last_msg:
                conversation.last_message_at = last_msg.created_at
                conversation.last_message_text = last_msg.message[:100] if last_msg.message else ""
                conversation.last_message_sender_id = last_msg.sender_id
                
                # Okunmamış mesaj sayılarını hesapla
                # User1 için okunmamış (user2'den gelen ve okunmamış)
                unread_for_user1 = Message.query.filter_by(
                    conversation_id=conversation.id,
                    sender_id=conversation.user2_id
                ).filter(Message.read_at.is_(None)).count()
                
                # User2 için okunmamış (user1'den gelen ve okunmamış)
                unread_for_user2 = Message.query.filter_by(
                    conversation_id=conversation.id,
                    sender_id=conversation.user1_id
                ).filter(Message.read_at.is_(None)).count()
                
                conversation.unread_count_user1 = unread_for_user1
                conversation.unread_count_user2 = unread_for_user2
        
        db.session.commit()
        
        # 5. İstatistikler
        print("\n" + "="*50)
        print("✨ Migration tamamlandı!")
        print("="*50)
        print(f"📊 Toplam Conversation: {Conversation.query.count()}")
        print(f"📨 Migrate edilen mesaj: {migrated_count}")
        print(f"📬 Toplam mesaj: {Message.query.count()}")
        print("\n💡 Öneriler:")
        print("   - Flask uygulamasını yeniden başlatın")
        print("   - Chat UI'ı test edin")
        print("   - Eski mesaj UI'ları kaldırılabilir")
        print("="*50)

if __name__ == '__main__':
    migrate_to_chat_system()
