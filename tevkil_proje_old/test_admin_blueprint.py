#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Admin Blueprint registration"""

from app import app

print("✅ Registered Blueprints:", list(app.blueprints.keys()))
print("\n📋 Admin Routes:")
admin_routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('admin.')]
for route in admin_routes:
    print(f"  {route.rule} -> {route.endpoint}")

print(f"\n✅ Total Admin Routes: {len(admin_routes)}")
