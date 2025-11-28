#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Remaining Routes in app.py"""

import os
os.environ['DEV_MODE'] = '1'

from app import app

print("=" * 80)
print("📝 REMAINING ROUTES IN app.py")
print("=" * 80)

# Find all routes that are NOT in blueprints
app_routes = []
for rule in app.url_map.iter_rules():
    endpoint = rule.endpoint
    # Skip static and blueprint routes
    if endpoint != 'static' and '.' not in endpoint:
        methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        app_routes.append((rule.rule, methods, endpoint))

print(f"\n✅ Total Routes in app.py: {len(app_routes)}")
print("-" * 80)

for route, methods, endpoint in sorted(app_routes, key=lambda x: x[0]):
    print(f"  {route:50s} [{methods:15s}] -> {endpoint}")

print("\n" + "=" * 80)
print("📊 ROUTE BREAKDOWN:")
print("=" * 80)
print(f"  Blueprint Routes: 59 routes")
print(f"  app.py Routes:    {len(app_routes)} routes")
print(f"  TOTAL:           {59 + len(app_routes)} routes")
print("=" * 80)

# Categorize remaining routes
categories = {
    'Settings': [],
    'Notifications': [],
    'Messages': [],
    'WhatsApp': [],
    'Security': [],
    'Other': []
}

for route, methods, endpoint in app_routes:
    if '/settings' in route:
        categories['Settings'].append((route, endpoint))
    elif '/notifications' in route:
        categories['Notifications'].append((route, endpoint))
    elif '/messages' in route:
        categories['Messages'].append((route, endpoint))
    elif '/whatsapp' in route:
        categories['WhatsApp'].append((route, endpoint))
    elif '/security' in route:
        categories['Security'].append((route, endpoint))
    else:
        categories['Other'].append((route, endpoint))

print("\n🗂️  CATEGORY BREAKDOWN:")
print("-" * 80)
for category, routes in categories.items():
    if routes:
        print(f"\n  {category} ({len(routes)} routes):")
        for route, endpoint in routes:
            print(f"    • {route:45s} -> {endpoint}")

print("\n" + "=" * 80)
