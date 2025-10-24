#!/usr/bin/env python3
"""Fly.io production veritabanındaki tabloları kontrol et"""
import os
from sqlalchemy import create_engine, inspect

# PostgreSQL URL fix
database_url = os.getenv('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"🔗 Bağlanılan DB: {database_url.split('@')[1] if '@' in database_url else 'N/A'}")

engine = create_engine(database_url)
inspector = inspect(engine)
tables = sorted(inspector.get_table_names())

print(f"\n📊 Toplam {len(tables)} tablo bulundu:")
for table in tables:
    print(f"   ✓ {table}")

print(f"\n🔍 tevkil_posts tablosu {'✅ VAR' if 'tevkil_posts' in tables else '❌ YOK'}")
