#!/usr/bin/env python3
"""Test script to verify auth routes are properly defined."""

try:
    print("Testing auth routes import...")
    from src.api.v1.auth_routes import router
    print("[SUCCESS] Auth routes imported successfully")

    print("\nChecking routes in the router:")
    for route in router.routes:
        print(f"  - {route.path} ({getattr(route, 'methods', 'N/A')})")

    print("\nTesting main app import...")
    from src.main import app
    print("[SUCCESS] Main app imported successfully")

    print("\nChecking all routes in main app:")
    auth_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'auth' in route.path.lower():
            auth_routes.append((route.path, getattr(route, 'methods', 'N/A')))

    for path, methods in auth_routes:
        print(f"  - {path} ({methods})")

    print(f"\nFound {len(auth_routes)} auth routes")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()