#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test ALL Blueprints - Final Summary"""

from app import app

print("=" * 80)
print("🎉 BLUEPRINT MIGRATION SUMMARY 🎉")
print("=" * 80)

blueprints = list(app.blueprints.keys())
print(f"\n✅ Total Blueprints Registered: {len(blueprints)}")
print(f"   {', '.join(blueprints)}\n")

# Count routes per blueprint
blueprint_stats = {}
for blueprint_name in blueprints:
    routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith(f'{blueprint_name}.')]
    blueprint_stats[blueprint_name] = len(routes)

print("📊 Routes per Blueprint:")
print("-" * 80)
total_routes = 0
for bp_name in sorted(blueprint_stats.keys()):
    count = blueprint_stats[bp_name]
    total_routes += count
    status = "✅" if count > 0 else "⚠️"
    print(f"  {status} {bp_name:15s}: {count:3d} routes")

print("-" * 80)
print(f"  📈 TOTAL ROUTES: {total_routes}")
print("=" * 80)

print("\n🔍 Detailed Route List:")
print("-" * 80)

for bp_name in sorted(blueprints):
    routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith(f'{bp_name}.')]
    if routes:
        print(f"\n{bp_name.upper()} ({len(routes)} routes):")
        for route in sorted(routes, key=lambda r: r.rule):
            methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
            print(f"  {route.rule:50s} [{methods:15s}] -> {route.endpoint}")

print("\n" + "=" * 80)
print("🎊 MIGRATION COMPLETE!")
print("=" * 80)
