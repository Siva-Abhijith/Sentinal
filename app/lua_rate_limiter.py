import time
from pathlib import Path

from app.redis_client import redis_client


class LuaRateLimiter:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate

        script_path = Path(__file__).parent / "lua" / "token_bucket.lua"
        script = script_path.read_text()

        self.script = redis_client.register_script(script)

    def allow(self, client_id: str) -> bool:
        key = f"rate_limit:{client_id}"
        now = time.monotonic()

        result = self.script(
            keys=[key],
            args=[
                self.capacity,
                self.refill_rate,
                now,
            ],
        )

        allowed = int(result[0])

        return allowed == 1
