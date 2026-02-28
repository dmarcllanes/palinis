import asyncpg
from config import DATABASE_URL

_pool = None


async def init_pool():
    global _pool
    if not DATABASE_URL:
        print("[DB] WARNING: DATABASE_URL not set. DB features disabled.")
        return
    _pool = await asyncpg.create_pool(DATABASE_URL)


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()


def get_pool():
    return _pool
