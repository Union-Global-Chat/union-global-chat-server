from aiomysql import Pool

from inspect import getmembers, isfunction, iscoroutinefunction
from functools import wraps


class DatabaseManager:
    pool: Pool

    def __init_subclass__(cls):
        for name, func in getmembers(cls, isfunction):
            if not name.startswith("_") and iscoroutinefunction(func):
                setattr(cls, name, cls.make_new_func(func))

    @staticmethod
    def make_new_func(func):
        @wraps(func)
        async def new_func(self, *args, **kwargs):
            if "cursor" in kwargs:
                return await func(self, *args, **kwargs)
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    return await func(self, cursor, *args, **kwargs)
        return new_func
