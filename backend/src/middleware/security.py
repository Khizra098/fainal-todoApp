"""
Security middleware for the verification system.
This module provides security headers and protection mechanisms.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import hashlib
import secrets
import re


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Prevent MIME-type sniffing
        if "Content-Type" not in response.headers:
            response.headers["Content-Type"] = "application/json"

        return response


class CORSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle CORS and related security.
    Note: FastAPI CORSMiddleware is used in main.py for production-grade CORS handling.
    This is kept for additional validation if needed.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        # CORS is handled by FastAPI's CORSMiddleware in main.py
        return response


class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add Content Security Policy header
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Basic CSP header (can be customized based on needs)
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.example.com; "
            "frame-ancestors 'none'; "
            "object-src 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate input for common attack patterns
    """
    def __init__(self, app, blocked_patterns=None):
        super().__init__(app)
        self.blocked_patterns = blocked_patterns or [
            r'<script[^>]*>',  # Basic XSS patterns
            r'javascript:',     # JavaScript URLs
            r'on\w+\s*=',      # Event handlers
            r'<iframe[^>]*>',   # iframe tags
            r'<object[^>]*>',   # object tags
            r'<embed[^>]*>',    # embed tags
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # For GET requests, check query parameters
        if request.method in ["GET"]:
            for param, value in request.query_params.items():
                if self._contains_blocked_pattern(str(value)):
                    return JSONResponse(
                        status_code=400,
                        content={"error": {"code": "INPUT_VALIDATION_ERROR", "message": "Invalid input detected", "details": {}}},
                    )

        # For POST/PUT requests, we'd typically check the body content
        # This is a simplified version - in practice, you'd want more sophisticated validation

        response = await call_next(request)
        return response

    def _contains_blocked_pattern(self, text: str) -> bool:
        """
        Check if text contains any blocked patterns
        """
        for pattern in self.blocked_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


def add_security_middleware(app):
    """
    Add all security middlewares to the FastAPI application
    """
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CORSProtectionMiddleware)
    app.add_middleware(ContentSecurityPolicyMiddleware)
    app.add_middleware(InputValidationMiddleware)

    return app