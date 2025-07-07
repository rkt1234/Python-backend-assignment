from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the async SQLAlchemy connection string
DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
SYNC_DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"


# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Optional: Async DB connection test function (do not run here!)
async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda x: None)
        print("✅ Async DB connection successful!")
    except Exception as e:
        print(f"❌ Async DB connection failed: {e}")

# Create async session maker
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for all ORM models
Base = declarative_base()

# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
