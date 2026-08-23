from concurrent.futures import ThreadPoolExecutor
import uuid

from app.lua_rate_limiter import LuaRateLimiter
from app.redis_client import redis_client


def test_lua_rate_limiter_is_atomic():
    client_id = f"lua-race-{uuid.uuid4()}"
    key = f"rate_limit:{client_id}"

    limiter = LuaRateLimiter(
        capacity=1,
        refill_rate=0,
    )

    def make_request(_):
        return limiter.allow(client_id)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(make_request, range(20)))

    allowed = sum(results)

    print(f"\nAllowed requests: {allowed}")

    redis_client.delete(key)

    assert allowed == 1
