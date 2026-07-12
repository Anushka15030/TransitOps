"""
Basic in-memory per-IP rate limiter, focused on the auth endpoints where
brute-force credential stuffing is the realistic threat. For a hackathon
+ enterprise-leaning demo this is appropriate; a production deployment
would back this with Redis instead of an in-process dict.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        self._hits[client_ip] = [t for t in self._hits[client_ip] if t > window_start]

        if len(self._hits[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again shortly.",
            )

        self._hits[client_ip].append(now)


auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)