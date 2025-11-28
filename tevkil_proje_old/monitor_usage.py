#!/usr/bin/env python3
"""
Fly.io Kaynak Kullanımı İzleme
Kullanım: python monitor_usage.py
"""
import subprocess
import json
import time
from datetime import datetime

def check_metrics():
    """Fly.io metrics kontrolü"""
    try:
        # Machine durumu
        result = subprocess.run(
            ['fly', 'status', '--app', 'tevkil', '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"\n{'='*60}")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # Machine info
            for machine in data.get('Machines', []):
                print(f"\n🖥️  Machine: {machine.get('id')}")
                print(f"   Region: {machine.get('region')}")
                print(f"   State: {machine.get('state')}")
                
                # Health checks
                checks = machine.get('checks', [])
                passing = sum(1 for c in checks if c.get('status') == 'passing')
                total = len(checks)
                print(f"   Health: {passing}/{total} passing")
        
        # Logs son 10 satır
        print(f"\n📋 Son Log Satırları:")
        log_result = subprocess.run(
            ['fly', 'logs', '--app', 'tevkil', '--no-tail'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if log_result.returncode == 0:
            lines = log_result.stdout.strip().split('\n')[-10:]
            for line in lines:
                print(f"   {line}")
                
    except subprocess.TimeoutExpired:
        print("❌ Timeout - Fly CLI yanıt vermiyor")
    except json.JSONDecodeError:
        print("❌ JSON parse hatası")
    except Exception as e:
        print(f"❌ Hata: {e}")

def monitor_loop(interval=300):
    """5 dakikada bir kontrol et"""
    print("🚀 Tevkil Monitoring Başlatıldı")
    print(f"⏱️  Kontrol aralığı: {interval} saniye")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            check_metrics()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring durduruldu")

if __name__ == '__main__':
    # Tek seferlik kontrol
    check_metrics()
    
    # Sürekli izleme için:
    # monitor_loop(interval=300)  # 5 dakika
