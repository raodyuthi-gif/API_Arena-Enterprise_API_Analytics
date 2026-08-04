"""Redis-backed sliding-window rate limiter middleware."""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter (replace with Redis in production)."""

    _counters: dict = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health and metrics endpoints
        if request.url.path in ("/", "/health", "/metrics", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        window_key = f"{client_ip}:{int(time.time() // 60)}"

        self._counters[window_key] = self._counters.get(window_key, 0) + 1

        if self._counters[window_key] > settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Max {settings.RATE_LIMIT_PER_MINUTE} requests/minute."
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, settings.RATE_LIMIT_PER_MINUTE - self._counters[window_key])
        )
        return response
