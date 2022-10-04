from aiomysql import Pool

from inspect import getmembers, isfunction
from functools import wraps


class DatabaseManager:
    pool: Pool

    def __init_subclass__(cls):
        for name, func in getmembers(cls, isfunction):
            if not name.startswith("_"):
                @wraps(func)
                async def new(*args, **kwargs):
                    async with cls.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            return await func(cur, *args, **kwargs)
                setattr(name, cls, func)
