import asyncpg


class Db:
    """Envoltorio mínimo sobre el pool de conexiones de asyncpg."""

    pool: asyncpg.Pool | None = None

    async def connect(self, db_url: str):
        # Crea un pool: varias conexiones que se reutilizan entre peticiones.
        self.pool = await asyncpg.create_pool(dsn=db_url)

    async def close(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None


db = Db()


async def get_connection():
    """Dependencia de FastAPI: cede una conexión del pool a cada petición."""
    async with db.pool.acquire() as conn:
        yield conn