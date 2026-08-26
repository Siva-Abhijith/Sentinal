import os
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest
from redis.exceptions import RedisError

from app.lua_rate_limiter import LuaRateLimiter


app = FastAPI()


rate_limiter = LuaRateLimiter(
    capacity=float(os.getenv("RATE_LIMIT_CAPACITY", "5")),
    refill_rate=float(os.getenv("RATE_LIMIT_REFILL_RATE", "1")),
)


requests_total = Counter(
    "sentinel_requests_total",
    "Total number of requests processed by Sentinel",
)

rate_limit_rejected_total = Counter(
    "sentinel_rate_limit_rejected_total",
    "Total number of requests rejected by the rate limiter",
)

rate_limiter_errors_total = Counter(
    "sentinel_rate_limiter_errors_total",
    "Total number of rate limiter backend errors",
)

request_duration_seconds = Histogram(
    "sentinel_request_duration_seconds",
    "Request processing duration in seconds",
)

responses_total = Counter(
    "sentinel_responses_total",
    "Total number of HTTP responses returned by Sentinel",
    ["status"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in {"/health", "/metrics"}:
        return await call_next(request)

    start = perf_counter()
    requests_total.inc()

    try:
        try:
            allowed = rate_limiter.allow(request.client.host)
        except RedisError:
            rate_limiter_errors_total.inc()
            responses_total.labels(status="503").inc()

            return JSONResponse(
                status_code=503,
                content={"detail": "Rate limiter unavailable"},
            )

        if not allowed:
            rate_limit_rejected_total.inc()
            responses_total.labels(status="429").inc()

            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
                headers={"Retry-After": "1"},
            )

        response = await call_next(request)
        responses_total.labels(status=str(response.status_code)).inc()

        return response

    finally:
        request_duration_seconds.observe(perf_counter() - start)


@app.get("/")
async def home():
    return {"message": "Sentinel is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4",
    )