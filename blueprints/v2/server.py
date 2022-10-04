from sanic import Blueprint
from lib import authorized, json
from aiofiles import open as aioopen
import lib
from tinydb import TinyDB, Query
from orjson import dumps, loads
from time import time
import asyncio
import zlib
import re
from utils.wsmanager import WsManager


bp = Blueprint("version_1", url_prefix="/api/v2")
manager = WsManager()
app = None


db = TinyDB('db.json')
token_table = db.table("token")
content_table = db.table("content")
status_table = db.table("status")
user = Query()
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

wss = []
            
@lib.loop(10)
async def status_check():
    status_table.insert({"time": int(time()), "count": len(wss)})


@bp.websocket("/gateway")
async def gateway(request, ws):
    """
    The gateway is the main connection point between the client and the server.
    It is responsible for receiving the client's messages and sending them to
    the right place.
    """
    await ws.send(dumper("hello"))
    while True:
        data = loads(zlib.decompress(await ws.recv()))
        if data["type"] == "identify":
            token = token_table.search(user.token == data["data"]["token"])
            if len(token) == 0:
                await ws.close(message=dumper("identify", success=False, code=4001, message="invaild token"))
            else:
                await ws.send(dumper("identify"))
                manager.connect(ws)
                app.loop.create_task(HeartBeat(ws).start())

@bp.post("/messages")
@authorized()
async def send(request, userid):
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
            "source": userid,
            "data": data
        }
    }
    await manager.broadcast(dumper(**payload))
    data["source"] = userid
    content_table.insert(data)
    return json(message="send message")
                    
@bp.get("/messages")
@authorized()
async def contents(request, userid):
    return json(content_table.all())

@bp.get("/messages/<message_id>")
@authorized()
async def getUser(self, userid, message_id):
    query = Query()
    data = content_table.search(query.message.id == message_id)
    if len(data) == 0:
        return json(message="I can't found that message.", status=404)
    else:
        return json(data[0])

@bp.delete("/messages/<message_id>")
@authorized()
async def delete_content(request, userid, message_id):
    data = content_table.search(content.message.id == message_id)
    if len(data) == 0:
        return json(status=404, message="I can't found that message.")
    else:
        check = content_table.search(content.from_bot == userid)
        if len(check) == 0:
            return json(status=403, message="Sended by another bot, so you can't delete message.")
        payload = {
            "type": "delete",
            "data": {
                "source": userid,
                "messageid": message_id
            }
        }
        await manager.broadcast(dumper(**payload))
        content_table.remove(content.message.id == message_id)
        return json()

@bp.get("/status")
async def status(request):
    return json(status_table.all())
