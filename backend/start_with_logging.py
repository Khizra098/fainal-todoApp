#!/usr/bin/env python3
"""Script to start the server with full error logging."""

import sys
import traceback
import logging

# Set up logging to capture everything
logging.basicConfig(level=logging.DEBUG)

try:
    from src.main import app
    import uvicorn

    print("Application imported successfully")

    # Try to generate OpenAPI to see if there are errors
    from fastapi.openapi.utils import get_openapi
    try:
        schema = get_openapi(title="Test", version="1.0", routes=app.routes)
        print(f"OpenAPI schema generated successfully. Paths: {list(schema.get('paths', {}).keys())}")

        # Check specifically for auth/profile
        if '/auth/profile' in schema.get('paths', {}):
            print("✓ /auth/profile endpoint is available in OpenAPI schema")
        else:
            print("✗ /auth/profile endpoint is NOT in OpenAPI schema")

    except Exception as e:
        print(f"Error generating OpenAPI schema: {e}")
        traceback.print_exc()

    # Start the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=False  # Disable reload to avoid interference
    )

except ImportError as e:
    print(f"Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"General error: {e}")
    traceback.print_exc()
    sys.exit(1)