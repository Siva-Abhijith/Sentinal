import os

import redis

from app.lua_rate_limiter import LuaRateLimiter


def test_shared_bucket_across_instances():
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )

    key = "rate_limit:test-distributed"
    client.delete(key)

    limiter_1 = LuaRateLimiter(capacity=5, refill_rate=0)
    limiter_2 = LuaRateLimiter(capacity=5, refill_rate=0)

    results = []

    for _ in range(3):
        results.append(limiter_1.allow("test-distributed"))

    for _ in range(3):
        results.append(limiter_2.allow("test-distributed"))

    assert results == [
        True,
        True,
        True,
        True,
        True,
        False,
    ]

    client.delete(key)
