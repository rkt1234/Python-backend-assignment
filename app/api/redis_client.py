import os
import redis.asyncio as redis
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Redis client
r = redis.from_url(REDIS_URL, decode_responses=True)
