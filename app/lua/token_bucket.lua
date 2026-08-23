local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local tokens = tonumber(redis.call("HGET", key, "tokens"))
local last_refill = tonumber(redis.call("HGET", key, "last_refill_time"))

if tokens == nil then
    tokens = capacity
    last_refill = now
end

local elapsed = now - last_refill
local tokens_to_add = elapsed * refill_rate

tokens = math.min(capacity, tokens + tokens_to_add)

local allowed = 0

if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

redis.call(
    "HSET",
    key,
    "tokens",
    tokens,
    "last_refill_time",
    now
)

return {allowed, tokens}