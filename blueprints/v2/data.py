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
            CREATE TABLE IF NOT EXISTS Token(
                BotId BIGINT,
                Token TEXT
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
    
    async def create_token(self, bot_id: int, token: str):
        await cursor.execute(
            "INSERT INTO Token VALUES (%s, %s);",
            (bot_id, token)
        )
