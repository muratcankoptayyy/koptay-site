"""Simple Flask runner without watchdog"""
from app import app

if __name__ == '__main__':
    print("🚀 Flask başlatılıyor...")
    print("📡 Webhook: http://127.0.0.1:5000/api/whatsapp/webhook")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
