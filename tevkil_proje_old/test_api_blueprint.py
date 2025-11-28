#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test API Blueprint registration"""

from app import app

print("✅ Registered Blueprints:", list(app.blueprints.keys()))
print("\n📋 API Routes:")
api_routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('api.')]
for route in api_routes:
    methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
    print(f"  {route.rule} [{methods}] -> {route.endpoint}")

print(f"\n✅ Total API Routes: {len(api_routes)}")
