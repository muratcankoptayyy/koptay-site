"""
Database Connection Pooling
For high concurrency
"""

# SQLAlchemy Engine Config
DATABASE_CONFIG = {
    'pool_size': 20,           # Standart connection pool
    'max_overflow': 40,        # Ekstra acil durumda
    'pool_timeout': 30,        # Connection bekleme süresi
    'pool_recycle': 3600,      # 1 saatte bir recycle
    'pool_pre_ping': True,     # Connection sağlık kontrolü
    'echo': False              # SQL log kapalı (production)
}

# app.py'de kullanım:
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = DATABASE_CONFIG
