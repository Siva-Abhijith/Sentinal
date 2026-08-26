from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

from app.lua_rate_limiter import LuaRateLimiter

app = FastAPI()

rate_limiter = LuaRateLimiter(
    capacity=5,
    refill_rate=1,
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_id = request.client.host

    try:
        allowed = rate_limiter.allow(client_id)
    except RedisError:
        return JSONResponse(
            status_code=503,
            content={"detail": "Rate limiter unavailable"},
        )

    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"},
        )

    return await call_next(request)


@app.get("/")
async def home():
    return {"message": "Sentinel is running"}