from typing import Optional, Tuple

from utils import DatabaseManager

from sanic import Sanic


class DataManager(DatabaseManager):
    def __init__(self, app: Sanic):
        self.pool = app.ctx.pool

    async def prepare_table(self, cursor):
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Message(
                Source BIGINT,
                Channel JSON,
                Author JSON,
                Guild JSON,
                Message JSON
            );""")
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS User(
                Id TEXT,
                UserName TEXT
            );
        """)

    async def create_message(self, cursor, source, channel, author, guild, message):
        await cursor.execute(
            "INSERT INTO Message VALUES (%s, %s, %s, %s, %s);",
            (source, channel, author, guild, message)
        )

    async def search_message(self, cursor, message_id):
        await cursor.execute(
            'SELECT * FROM Message WHERE Message -> "$.id" = %s;',
            (message_id,)
        )
        return await cursor.fetchone()
    
    async def get_bot(self, bot_id: int) -> Optional[Tuple[str, str]]:
        await cursor.execute(
            "SELECT * FROM User WHERE Id=%s;",
            (bot_id,)
        )
        return await cursor.fetchone()
