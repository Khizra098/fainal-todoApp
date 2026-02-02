"""
Rate limiting middleware for the verification system.
This module provides rate limiting functionality to prevent abuse.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from collections import defaultdict, deque
import hashlib


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm
    """
    def __init__(self, requests: int, window_size: int):
        """
        Initialize rate limiter

        Args:
            requests: Number of requests allowed per window
            window_size: Window size in seconds
        """
        self.requests = requests
        self.window_size = window_size
        self.storage = defaultdict(deque)  # ip -> list of timestamps

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for given identifier

        Args:
            identifier: Unique identifier for the client (e.g., IP address)

        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - self.window_size

        # Clean old requests outside the window
        while self.storage[identifier] and self.storage[identifier][0] < window_start:
            self.storage[identifier].popleft()

        # Check if we're under the limit
        if len(self.storage[identifier]) < self.requests:
            self.storage[identifier].append(now)
            return True

        return False

    def get_reset_time(self, identifier: str) -> float:
        """
        Get the time when the rate limit resets for the identifier

        Args:
            identifier: Unique identifier for the client

        Returns:
            float: Unix timestamp when the rate limit will reset
        """
        if self.storage[identifier]:
            return self.storage[identifier][0] + self.window_size
        return time.time()


# Predefined rate limiters for different endpoints
STANDARD_LIMITER = RateLimiter(requests=100, window_size=60)  # 100 requests per minute
HEAVY_COMPUTE_LIMITER = RateLimiter(requests=10, window_size=60)  # 10 requests per minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware that applies different limits based on endpoint
    """
    def __init__(self, app, standard_limiter=None, heavy_compute_limiter=None):
        super().__init__(app)
        self.standard_limiter = standard_limiter or STANDARD_LIMITER
        self.heavy_compute_limiter = heavy_compute_limiter or HEAVY_COMPUTE_LIMITER

        # Define which endpoints are considered "heavy compute"
        self.heavy_compute_endpoints = [
            "/api/v1/performance/benchmarks",
            "/api/v1/security/scans",
            "/api/v1/verification/features",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Determine which limiter to use based on endpoint
        limiter = self._get_limiter_for_endpoint(request.url.path)

        if not limiter.is_allowed(client_ip):
            reset_time = limiter.get_reset_time(client_ip)
            retry_after = int(reset_time - time.time())

            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded. Please try again later.",
                        "details": {
                            "retry_after": retry_after
                        }
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limiter.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time))
                }
            )

        # Add rate limit headers to response
        response = await call_next(request)

        # Calculate remaining requests
        now = time.time()
        window_start = now - limiter.window_size
        # Clean old requests to get accurate count
        while limiter.storage[client_ip] and limiter.storage[client_ip][0] < window_start:
            limiter.storage[client_ip].popleft()

        remaining = limiter.requests - len(limiter.storage[client_ip])
        reset_time = now + limiter.window_size

        response.headers["X-RateLimit-Limit"] = str(limiter.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request
        """
        # Check for forwarded-for header first (for proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP if multiple are provided
            return forwarded_for.split(",")[0].strip()

        # Fall back to direct client IP
        client_host = request.client.host if request.client else "127.0.0.1"
        return client_host

    def _get_limiter_for_endpoint(self, path: str) -> RateLimiter:
        """
        Determine which rate limiter to use based on the endpoint path

        Args:
            path: Request path

        Returns:
            RateLimiter: Appropriate rate limiter for the endpoint
        """
        for endpoint in self.heavy_compute_endpoints:
            if path.startswith(endpoint):
                return self.heavy_compute_limiter

        return self.standard_limiter


def add_rate_limiting_middleware(app):
    """
    Add rate limiting middleware to the FastAPI application
    """
    app.add_middleware(RateLimitMiddleware)
    return app