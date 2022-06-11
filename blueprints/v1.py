from sanic import Blueprint
from lib import authorized, json
import lib
from tinydb import TinyDB, Query
from orjson import dumps, loads
from time import time
import asyncio
import zlib


bp = Blueprint("version_1", url_prefix="/api/v1")
app = None

db = TinyDB('db.json')
token_table = db.table("token")
content_table = db.table("content")
status_table = db.table("status")
user = Query()
content = Query()

def dumper(type: str, data: dict=None, *, success: bool=True, message: str=None):
    payload = {
        "type": type,
        "data": data,
        "success": success,
        "message": message
    }
    return zlib.compress(dumps(payload))
wss = []

class HeartBeat:
    def __init__(self, ws):
        self.ws = ws

    async def send_heartbeat(self):
        await self.ws.send(dumper('heartbeat', {"unix_time": time()}))

    async def sending_heartbeat(self):
        while True:
            try:
                await self.send_heartbeat()
            except Exception:
                wss.remove(self.ws)
                break
            await asyncio.sleep(10)
            
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
                wss.append(ws)
                app.loop.create_task(HeartBeat(ws).sending_heartbeat())

@bp.post("/messages")
@authorized()
async def send(request, userid):
    data = request.json
    if "discord.gg" in data["message"]["content"]:
        return json(message="Detect invite link", status=400)
    payload = {
        "type": "message",
        "data": {
            "source": userid,
            "data": data
        }
    }
    for ws in wss:
        try:
            await ws.send(dumper(**payload))
        except Exception:
            wss.remove(ws)
    data["from_bot"] = userid
    content_table.insert(data)
    return json(message="送信できました")
                    
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
        return json(message="メッセージが見当たりません", status=404)
    else:
        return json(data[0])

@bp.delete("/messages/<message_id>")
@authorized()
async def delete_content(request, userid, message_id):
    data = content_table.search(content.message.id == message_id)
    if len(data) == 0:
        return json(status=404, message="そのメッセージは見つかりません")
    else:
        check = content_table.search(content.from_bot == userid)
        if len(check) == 0:
            return json(status=401, message="別のbotから送信されていますので、削除できません。")
        payload = {
            "type": "delete",
            "data": {
                "source": userid,
                "messageid": message_id
            }
        }
        for ws in wss:
            try:
                await ws.send(dumper(**payload))
            except Exception:
                wss.remove(ws)
        content_table.remove(content.message.id == message_id)
        return json()

@bp.get("/status")
async def status(request):
    return json(status_table.all())
