import asyncpg
from config import DATABASE_URL

_pool = None


async def init_pool():
    global _pool
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    _pool = await asyncpg.create_pool(DATABASE_URL, ssl="require")
    print("[DB] Connection pool created.")


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()


def get_pool():
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Check DATABASE_URL.")
    return _pool
