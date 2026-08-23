import uuid

from app.lua_rate_limiter import LuaRateLimiter
from app.redis_client import redis_client


def test_lua_rate_limiter_allows_and_rejects():
    client_id = f"lua-test-{uuid.uuid4()}"
    key = f"rate_limit:{client_id}"

    limiter = LuaRateLimiter(
        capacity=2,
        refill_rate=1,
    )

    assert limiter.allow(client_id) is True
    assert limiter.allow(client_id) is True
    assert limiter.allow(client_id) is False

    redis_client.delete(key)
