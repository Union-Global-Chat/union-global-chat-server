from sanic import Blueprint
from lib import json
from aiofiles import open as aioopen
import jwt
from jwt.exceptions import InvalidSignatureError
import lib
from tinydb import TinyDB, Query
from orjson import dumps, loads
from sanic.log import logger
from time import time
import asyncio
import zlib
import re
from utils.wsmanager import WsManager

from .utils import HeartBeat, authorized
from .data import DataManager
from .errors import InvalidTokenError
from data import CONFIG


bp = Blueprint("version_2", url_prefix="/api/v2")
manager = WsManager()
app = None
data: DataManager | None = None


db = TinyDB('db.json')
content_table = db.table("content")
content = Query()


invite_detector = re.compile("(http(s)?://)?((canary|ptb).)?discord(.gg|.com)/[0-9]")


def dumper(type: str, data: dict=None, *, success: bool=True, message: str=None):
    payload = {
        "type": type,
        "data": data,
        "success": success,
        "message": message
    }
    return zlib.compress(dumps(payload))
            

@bp.after_server_start
async def setup(app, _):
    data = DataManager(app)
    await data.prepare_table()


@bp.websocket("/gateway")
async def gateway(request, ws):
    """
    The gateway is the main connection point between the client and the server.
    It is responsible for receiving the client's messages and sending them to
    the right place.
    """
    await ws.send(dumper("hello"))
    while True:
        payload = loads(zlib.decompress(await ws.recv()))
        if data["type"] == "identify":
            try:
                user = jwt.decode(payload["data"]["token"], CONFIG["secret_key"], algorithms=["HS256"])
                if await data.get_bot(user["id"]) is None:
                    raise InvalidTokenError("Invalid token")
            except (
                InvalidSignatureError,
                InvalidTokenError
            ):
                await ws.close(message=dumper("identify", success=False, code=4001, message="invaild token"))
            else:
                await ws.send(dumper("identify"))
                manager.connect(ws)
                app.loop.create_task(HeartBeat(ws).start())


@bp.post("/messages")
@authorized
async def send(request, user):
    data = request.json
    async with aioopen("bans.txt", "r") as f:
        users = await f.readlines()
    if data["author"]["id"] in users:
        return json(message="That user are baned", status=400, code="ban_user")
    if invite_detector.match(data["message"]["content"]) is not None:
        return json(message="Invite link detected", status=400, code="ngword_detect")
    payload = {
        "type": "message",
        "data": {
            "source": user["id"],
            "data": data
        }
    }
    await manager.broadcast(dumper(**payload))
    data["source"] = userid
    logger.info(f"Recieve message: {data}")
    await data.create_message(**data)
    return json(message="send message")


@bp.get("/messages")
@authorized
async def contents(request, userid):
    return json(content_table.all())


@bp.get("/messages/<message_id>")
@authorized
async def getUser(self, userid, message_id):
    result = await data.search_message(message_id)
    if result is None:
        return json(message="I can't found that message.", status=404)
    else:
        source, channel, author, guild, message = result
        return json({
            "source": source,
            "channel": channel,
            "author": author,
            "guild": guild,
            "message": message
        })


@bp.delete("/messages/<message_id>")
@authorized
async def delete_content(request, user, message_id):
    data = content_table.search(content.message.id == message_id)
    if len(data) == 0:
        return json(status=404, message="I can't found that message.")
    else:
        check = content_table.search(content.from_bot == user["id"])
        if len(check) == 0:
            return json(status=403, message="Sended by another bot, so you can't delete message.")
        payload = {
            "type": "delete",
            "data": {
                "source": user["id"],
                "messageid": message_id
            }
        }
        await manager.broadcast(dumper(**payload))
        content_table.remove(content.message.id == message_id)
        return json()
