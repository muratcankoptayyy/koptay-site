#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Main Blueprint registration"""

from app import app

print("✅ Registered Blueprints:", list(app.blueprints.keys()))
print("\n📋 Main Routes:")
main_routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('main.')]
for route in main_routes:
    methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
    print(f"  {route.rule} [{methods}] -> {route.endpoint}")

print(f"\n✅ Total Main Routes: {len(main_routes)}")
