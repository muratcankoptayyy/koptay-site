#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Migration: Add is_verified column to User model"""

import os
os.environ['DEV_MODE'] = '1'

from app import app, db
from sqlalchemy import inspect, text

print("=" * 80)
print("🔧 DATABASE MIGRATION: Add is_verified column")
print("=" * 80)

with app.app_context():
    # Check if column exists
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    print("\n📋 Current User table columns:")
    print(f"  • verified: {'✅' if 'verified' in columns else '❌'}")
    print(f"  • is_verified: {'✅' if 'is_verified' in columns else '❌'}")
    
    if 'is_verified' in columns:
        print("\n✅ is_verified column already exists!")
        print("   No migration needed.")
    else:
        print("\n⚠️  is_verified column does not exist")
        print("   Adding column...")
        
        try:
            # Add the column
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0'))
                conn.commit()
            
            print("✅ Column added successfully!")
            
            # Sync verified -> is_verified for existing users
            print("\n📊 Syncing existing data...")
            with db.engine.connect() as conn:
                result = conn.execute(text('UPDATE users SET is_verified = verified'))
                conn.commit()
                print(f"   Synced {result.rowcount} users")
            
            print("\n✅ Migration complete!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("   This might be okay if using SQLite (it has ALTER TABLE limitations)")

print("\n" + "=" * 80)
print("🎉 DONE!")
print("=" * 80)
