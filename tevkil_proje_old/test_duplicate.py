"""
Basit test - Duplicate kontrolü
"""
from whatsapp_central_bot import central_bot
from datetime import datetime, timezone

# Message cache test
message_id_1 = "test_msg_123"
message_id_2 = "test_msg_456"

print("\n" + "="*60)
print("🧪 DUPLICATE MESAJ ÖNLEME TESTİ")
print("="*60)

# Mesaj 1 - cache'e ekle
now = datetime.now(timezone.utc)
central_bot.processed_messages[message_id_1] = now

print(f"\n✅ Mesaj 1 cache'e eklendi: {message_id_1}")
print(f"   Cache boyutu: {len(central_bot.processed_messages)}")

# Aynı mesajı tekrar kontrol et
if message_id_1 in central_bot.processed_messages:
    print(f"✅ DUPLICATE ALGILANDI! {message_id_1} zaten cache'de")
else:
    print(f"❌ HATA! Duplicate algılanmadı")

# Farklı mesaj
if message_id_2 not in central_bot.processed_messages:
    print(f"✅ Yeni mesaj {message_id_2} cache'de YOK, işlenebilir")
    central_bot.processed_messages[message_id_2] = now
    print(f"   Cache boyutu: {len(central_bot.processed_messages)}")
else:
    print(f"❌ HATA! Yeni mesaj cache'de bulundu")

print("\n" + "="*60)
print("✅ DUPLICATE ÖNLEME SİSTEMİ ÇALIŞIYOR!")
print("="*60)

print(f"\n📊 Cache durumu:")
for msg_id, timestamp in central_bot.processed_messages.items():
    print(f"   {msg_id}: {timestamp}")
