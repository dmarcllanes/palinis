from domain.cleaner import Cleaner
from uuid import UUID


async def get_all(pool) -> list[Cleaner]:
    rows = await pool.fetch(
        "SELECT * FROM cleaners ORDER BY created_at DESC"
    )
    return [Cleaner(**dict(row)) for row in rows]


async def get_by_id(pool, cleaner_id: UUID) -> Cleaner | None:
    row = await pool.fetchrow(
        "SELECT * FROM cleaners WHERE id = $1", cleaner_id
    )
    return Cleaner(**dict(row)) if row else None


async def get_by_username(pool, username: str) -> Cleaner | None:
    row = await pool.fetchrow(
        "SELECT * FROM cleaners WHERE username = $1", username
    )
    return Cleaner(**dict(row)) if row else None


async def add(pool, name: str, email: str, phone: str, username: str, password_hash: str) -> Cleaner:
    row = await pool.fetchrow(
        """
        INSERT INTO cleaners (name, email, phone, username, password_hash)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        name, email, phone, username, password_hash,
    )
    return Cleaner(**dict(row))


async def toggle_active(pool, cleaner_id: UUID, is_active: bool) -> Cleaner | None:
    row = await pool.fetchrow(
        "UPDATE cleaners SET is_active = $1 WHERE id = $2 RETURNING *",
        is_active, cleaner_id,
    )
    return Cleaner(**dict(row)) if row else None


async def delete(pool, cleaner_id: UUID) -> bool:
    result = await pool.execute(
        "DELETE FROM cleaners WHERE id = $1", cleaner_id
    )
    return result == "DELETE 1"


async def count_active(pool) -> int:
    row = await pool.fetchrow("SELECT COUNT(*) FROM cleaners WHERE is_active = true")
    return row[0]
