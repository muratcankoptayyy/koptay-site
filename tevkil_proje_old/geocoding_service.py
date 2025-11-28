"""
Geocoding Service - Google Maps API
Adres → Koordinat (lat/lng) dönüşümü
"""
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

def get_coordinates(address):
    """
    Adres string'ini lat/lng koordinatlarına çevir
    
    Args:
        address (str): Tam adres (örn: "Ankara Adliyesi, Ankara")
    
    Returns:
        dict: {'lat': float, 'lng': float, 'formatted_address': str} veya None
    """
    if not GOOGLE_MAPS_API_KEY:
        print('⚠️ GOOGLE_MAPS_API_KEY bulunamadı!')
        # Fallback: Şehir bazlı sabit koordinatlar
        return get_fallback_coordinates(address)
    
    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY,
            'language': 'tr',
            'region': 'tr'
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data['status'] == 'OK' and len(data['results']) > 0:
            location = data['results'][0]['geometry']['location']
            formatted_address = data['results'][0]['formatted_address']
            
            return {
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': formatted_address
            }
        else:
            print(f'⚠️ Geocoding failed: {data.get("status")} - {address}')
            return get_fallback_coordinates(address)
            
    except Exception as e:
        print(f'❌ Geocoding error: {e}')
        return get_fallback_coordinates(address)

def get_fallback_coordinates(address):
    """
    API olmadan şehir bazlı koordinat döndür
    """
    city_coords = {
        'ankara': {'lat': 39.9334, 'lng': 32.8597},
        'istanbul': {'lat': 41.0082, 'lng': 28.9784},
        'izmir': {'lat': 38.4237, 'lng': 27.1428},
        'bursa': {'lat': 40.1826, 'lng': 29.0665},
        'antalya': {'lat': 36.8969, 'lng': 30.7133},
        'adana': {'lat': 37.0000, 'lng': 35.3213},
        'konya': {'lat': 37.8667, 'lng': 32.4833},
        'gaziantep': {'lat': 37.0662, 'lng': 37.3833},
        'kayseri': {'lat': 38.7312, 'lng': 35.4787},
        'eskişehir': {'lat': 39.7767, 'lng': 30.5206},
    }
    
    # Adres içinde şehir ara
    address_lower = address.lower()
    for city, coords in city_coords.items():
        if city in address_lower:
            return {
                'lat': coords['lat'],
                'lng': coords['lng'],
                'formatted_address': address
            }
    
    # Bulunamazsa Ankara merkez
    return {
        'lat': 39.9334,
        'lng': 32.8597,
        'formatted_address': address
    }

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    İki koordinat arası mesafe hesapla (km)
    Haversine formülü
    
    Returns:
        float: Mesafe (km)
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Dünya yarıçapı (km)
    R = 6371.0
    
    lat1_rad = radians(lat1)
    lng1_rad = radians(lng1)
    lat2_rad = radians(lat2)
    lng2_rad = radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)

def get_directions_url(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Google Maps'te rota için URL oluştur
    
    Returns:
        str: Google Maps directions URL
    """
    return f'https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lng}&destination={dest_lat},{dest_lng}&travelmode=driving'

def geocode_courthouse(city, courthouse):
    """
    Adliye için koordinat al
    
    Args:
        city (str): Şehir adı
        courthouse (str): Adliye adı
    
    Returns:
        dict: Koordinatlar
    """
    address = f'{courthouse}, {city}, Türkiye'
    return get_coordinates(address)

def batch_geocode_posts(posts):
    """
    Birden fazla ilan için toplu geocoding
    
    Args:
        posts (list): TevkilPost listesi
    
    Returns:
        dict: {post_id: coordinates}
    """
    results = {}
    
    for post in posts:
        if hasattr(post, 'latitude') and post.latitude and post.longitude:
            # Zaten koordinatı var
            results[post.id] = {
                'lat': post.latitude,
                'lng': post.longitude
            }
        else:
            # Geocode et
            address = f'{post.courthouse}, {post.city}, Türkiye'
            coords = get_coordinates(address)
            
            if coords:
                results[post.id] = {
                    'lat': coords['lat'],
                    'lng': coords['lng']
                }
            
            # Rate limiting için kısa bekleme
            time.sleep(0.1)
    
    return results

# Test için
if __name__ == '__main__':
    print('🗺️ Geocoding Service Test')
    print('=' * 50)
    
    # Test 1: Ankara Adliyesi
    test_address = 'Ankara Adliye Sarayı, Ankara'
    print(f'Test: {test_address}')
    coords = get_coordinates(test_address)
    print(f'Sonuç: {coords}')
    print()
    
    # Test 2: İstanbul Çağlayan
    test_address2 = 'Çağlayan Adliyesi, İstanbul'
    print(f'Test: {test_address2}')
    coords2 = get_coordinates(test_address2)
    print(f'Sonuç: {coords2}')
    print()
    
    # Test 3: Mesafe hesaplama
    if coords and coords2:
        distance = calculate_distance(
            coords['lat'], coords['lng'],
            coords2['lat'], coords2['lng']
        )
        print(f'Ankara - İstanbul arası: {distance} km')
        print()
        
        # Test 4: Rota URL
        route_url = get_directions_url(
            coords['lat'], coords['lng'],
            coords2['lat'], coords2['lng']
        )
        print(f'Rota URL: {route_url}')
