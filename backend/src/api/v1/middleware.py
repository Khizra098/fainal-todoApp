"""
Middleware module for the AI Assistant Chat feature.
This module contains common middleware for the API.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """
    Middleware to log requests and responses
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        start_time = time.time()

        # Log the incoming request
        logger.info(f"Request: {request.method} {request.url}")

        # Create a response receiver that captures the response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                message.setdefault("headers", [])
                headers = dict(message["headers"])
                headers[b"X-Process-Time"] = str(process_time).encode()
                message["headers"] = [(k, v) for k, v in headers.items()]

            await send(message)

        await self.app(scope, receive, send_wrapper)

async def error_handler(request: Request, call_next: Callable[[Request], Awaitable]) -> JSONResponse:
    """
    Global error handler middleware
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"}
        )