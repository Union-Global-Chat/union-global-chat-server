from utils import DatabaseManager


class DataManager(DatabaseManager):
    def __init__(self, app: Sanic):
        self.pool = app.ctx.pool

    async def prepare_table(self, cursor):
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS Message(
                Source BIGINT,
                Channel JSON,
                Author JSON,
                Guild JSON
                Message JSON
            );""")

    async def create_message(self, cursor, source, channel, author, guild, message):
        await cursor.execute(
            "INSERT INTO Message VALUES (%s, %s, %s, %s, %s);",
            (source, channel, author, guild, message)
        )
