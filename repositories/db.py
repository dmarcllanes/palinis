import asyncpg
import urllib.parse
from config import DATABASE_URL

_pool = None


async def init_pool():
    global _pool
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    try:
        parsed = urllib.parse.urlparse(DATABASE_URL)
        print(f"[DB] Connecting to host={parsed.hostname} port={parsed.port} user={parsed.username}")
        _pool = await asyncpg.create_pool(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=urllib.parse.unquote(parsed.username),
            password=urllib.parse.unquote(parsed.password),
            database=parsed.path.lstrip("/"),
            ssl="require",
            statement_cache_size=0,
        )
        print("[DB] Connection pool created.")
    except Exception as e:
        print(f"[DB] ERROR: Could not connect to database: {e}")
        raise


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()


def get_pool():
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Check DATABASE_URL.")
    return _pool
