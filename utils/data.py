from aiomysql import Pool

from inspect import getmembers, isfunction, iscoroutinefunction
from functools import wraps


class DatabaseManager:
    pool: Pool

    def __init_subclass__(cls):
        for name, func in getmembers(cls, isfunction):
            if not name.startswith("_") and iscoroutinefunction(func):
                @wraps(func)
                async def new(self, *args, **kwargs):
                    if "cursor" in kwargs:
                        return await func(cur, *args, **kwargs)
                    async with self.pool.acquire() as conn:
                        async with conn.cursor() as cur:
                            return await func(cur, *args, **kwargs)
                setattr(cls, name, new)
