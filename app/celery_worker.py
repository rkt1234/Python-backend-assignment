import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

redis_url = os.getenv("REDIS_URL")

celery_app = Celery("worker", broker=redis_url, backend=redis_url)
