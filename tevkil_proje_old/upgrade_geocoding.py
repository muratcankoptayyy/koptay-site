"""
Database Migration: Add Geocoding Coordinates
Adds latitude, longitude, and formatted_address to TevkilPost
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import TevkilPost
from geocoding_service import get_coordinates
import time

def upgrade_geocoding():
    """Add geocoding columns to tevkil_posts table"""
    
    with app.app_context():
        print('🗺️ Harita Entegrasyonu - Database Migration')
        print('=' * 60)
        
        # Add columns using raw SQL
        try:
            print('\n📍 Yeni kolonlar ekleniyor...')
            
            with db.engine.connect() as conn:
                # Add latitude column
                try:
                    conn.execute(db.text('ALTER TABLE tevkil_posts ADD COLUMN latitude FLOAT'))
                    print('   ✅ latitude kolonu eklendi')
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print('   ⚠️ latitude kolonu zaten var')
                    else:
                        raise
                
                # Add longitude column
                try:
                    conn.execute(db.text('ALTER TABLE tevkil_posts ADD COLUMN longitude FLOAT'))
                    print('   ✅ longitude kolonu eklendi')
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print('   ⚠️ longitude kolonu zaten var')
                    else:
                        raise
                
                # Add formatted_address column
                try:
                    conn.execute(db.text('ALTER TABLE tevkil_posts ADD COLUMN formatted_address VARCHAR(300)'))
                    print('   ✅ formatted_address kolonu eklendi')
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print('   ⚠️ formatted_address kolonu zaten var')
                    else:
                        raise
                
                conn.commit()
            
            print('\n✅ Kolonlar başarıyla eklendi!')
            
        except Exception as e:
            print(f'\n❌ Kolon ekleme hatası: {e}')
            return False
        
        # Geocode existing posts
        try:
            print('\n🌍 Mevcut ilanlar geocoding yapılıyor...')
            
            posts = TevkilPost.query.filter(
                db.or_(
                    TevkilPost.latitude.is_(None),
                    TevkilPost.longitude.is_(None)
                )
            ).all()
            
            total_posts = len(posts)
            print(f'   📊 Toplam {total_posts} ilan geocode edilecek')
            
            success_count = 0
            failed_count = 0
            
            for i, post in enumerate(posts, 1):
                # Progress
                if i % 10 == 0 or i == total_posts:
                    print(f'   🔄 {i}/{total_posts} işleniyor...')
                
                # Build address
                address_parts = []
                if post.courthouse:
                    address_parts.append(post.courthouse)
                if post.district:
                    address_parts.append(post.district)
                if post.city:
                    address_parts.append(post.city)
                address_parts.append('Türkiye')
                
                address = ', '.join(address_parts)
                
                # Geocode
                coords = get_coordinates(address)
                
                if coords:
                    post.latitude = coords['lat']
                    post.longitude = coords['lng']
                    post.formatted_address = coords['formatted_address']
                    success_count += 1
                else:
                    failed_count += 1
                    print(f'      ❌ Geocoding başarısız: {address}')
                
                # Rate limiting (Google API limit: 50 req/sec)
                time.sleep(0.05)
            
            # Commit changes
            db.session.commit()
            
            print(f'\n✅ Geocoding tamamlandı!')
            print(f'   ✓ Başarılı: {success_count}')
            print(f'   ✗ Başarısız: {failed_count}')
            
        except Exception as e:
            print(f'\n❌ Geocoding hatası: {e}')
            db.session.rollback()
            return False
        
        print('\n' + '=' * 60)
        print('✨ Harita entegrasyonu migration tamamlandı!')
        print('=' * 60)
        return True

if __name__ == '__main__':
    success = upgrade_geocoding()
    sys.exit(0 if success else 1)
