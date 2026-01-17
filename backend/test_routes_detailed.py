#!/usr/bin/env python3
"""Direct test of the main application routes."""

import sys
import traceback
from src.main import app

def test_routes():
    print("Testing main application routes...")

    try:
        print(f"Number of routes in app: {len(app.routes)}")

        auth_routes = []
        for i, route in enumerate(app.routes):
            if hasattr(route, 'path'):
                path = route.path
                print(f"{i}: {path} - {type(route).__name__}")

                if 'auth' in path.lower():
                    auth_routes.append((path, route))

        print(f"\nFound {len(auth_routes)} auth-related routes:")
        for path, route in auth_routes:
            print(f"  - {path}")

        # Let's also check if there are any exceptions when accessing the OpenAPI spec programmatically
        print("\nTesting OpenAPI generation...")
        from fastapi.openapi.utils import get_openapi

        try:
            openapi_schema = get_openapi(
                title="Test API",
                version="1.0.0",
                routes=app.routes,
            )
            auth_paths = [path for path in openapi_schema.get('paths', {}).keys() if 'auth' in path.lower()]
            print(f"OpenAPI contains {len(auth_paths)} auth paths: {auth_paths}")
        except Exception as e:
            print(f"Error generating OpenAPI schema: {e}")
            traceback.print_exc()

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_routes()
    if success:
        print("\n[SUCCESS] Route test completed successfully")
    else:
        print("\n[ERROR] Route test failed")
        sys.exit(1)