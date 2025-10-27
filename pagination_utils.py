"""
Pagination Helper Utilities
Liste sayfaları için sayfalama desteği
"""

def paginate_query(query, page=1, per_page=20):
    """
    SQLAlchemy query'sine pagination ekle
    
    Args:
        query: SQLAlchemy query objesi
        page: Sayfa numarası (1'den başlar)
        per_page: Sayfa başına kayıt sayısı
        
    Returns:
        dict: {
            'items': [...],
            'total': int,
            'page': int,
            'per_page': int,
            'pages': int,
            'has_prev': bool,
            'has_next': bool,
            'prev_num': int|None,
            'next_num': int|None
        }
    """
    # Sayfa kontrolü
    if page < 1:
        page = 1
    
    # Total sayı
    total = query.count()
    
    # Toplam sayfa sayısı
    pages = (total + per_page - 1) // per_page
    
    # Eğer page çok büyükse son sayfaya git
    if page > pages and pages > 0:
        page = pages
    
    # Offset hesapla
    offset = (page - 1) * per_page
    
    # Items al
    items = query.limit(per_page).offset(offset).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'has_prev': page > 1,
        'has_next': page < pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < pages else None
    }

def get_page_numbers(current_page, total_pages, window=2):
    """
    Sayfalama için gösterilecek sayfa numaralarını hesapla
    
    Args:
        current_page: Mevcut sayfa
        total_pages: Toplam sayfa sayısı
        window: Her yönde gösterilecek sayfa sayısı
        
    Returns:
        list: Gösterilecek sayfa numaraları
    """
    if total_pages <= 1:
        return [1]
    
    # Başlangıç ve bitiş
    start = max(1, current_page - window)
    end = min(total_pages, current_page + window)
    
    pages = list(range(start, end + 1))
    
    # İlk sayfa eklenmemişse ekle
    if 1 not in pages:
        pages = [1, '...'] + pages
    
    # Son sayfa eklenmemişse ekle
    if total_pages not in pages:
        pages = pages + ['...', total_pages]
    
    return pages
