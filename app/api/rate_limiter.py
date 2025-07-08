from app.api.redis_client import r  # adjust path if needed

RATE_LIMIT = 3
WINDOW = 60  # seconds

async def is_rate_limited(user_id: str) -> bool:
    key = f"rate_limit:{user_id}"
    
    # Increment the request count
    current = await r.incr(key)

    if current == 1:
        # First request, set expiration
        await r.expire(key, WINDOW)

    if current > RATE_LIMIT:
        return True
    return False
