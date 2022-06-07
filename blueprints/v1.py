from sanic import Blueprint, response
from lib import authorized
from tinydb import TinyDB, Query
from orjson import dumps, loads
import asyncio
import zlib


bp = Blueprint("version_1", url_prefix="/api/v1")

db = TinyDB('db.json')
token_table = db.table("token")
content_table = db.table("content")
user = Query()
content = Query()

def dumper(data):
    return zlib.compress(dumps(data))
wss = []

class HeartBeat:
    def __init__(self, ws):
        self.ws = ws

    async def send_heartbeat(self):
        await self.ws.send(dumper({'type': 'heartbeat'}))

    async def sending_heartbeat(self):
        while True:
            try:
                await self.send_heartbeat()
            except Exception:
                wss.remove(self.ws)
                break
            await asyncio.sleep(10)

@bp.websocket("/gateway")
async def gateway(request, ws):
    """
    The gateway is the main connection point between the client and the server.
    It is responsible for receiving the client's messages and sending them to
    the right place.
    """
    await ws.send(dumper({"type": "hello"}))
    while True:
        data = loads(zlib.decompress(await ws.recv()))
        if data["type"] == "identify":
            token = token_table.search(user.token == data["token"])
            if len(token) == 0:
                await ws.send(dumper({"type": "identify", "success": False}))
                await ws.close()
            else:
                await ws.send(dumper({"type": "identify", "success": True}))
                wss.append(ws)
                app.loop.create_task(HeartBeat(ws).sending_heartbeat())

@bp.post("/channels")
@authorized()
async def send(request, userid):
    data = request.json
    payload = {
        "type": "send",
        "data": {
            "from": userid,
            "data": data
        }
    }
    try:
        await asyncio.gather(*[ws.send(dumper(payload)) for ws in wss])
    except Exception:
        pass
    data["from_bot"] = userid
    content_table.insert(data)
    return response.json({"success": True})
                    
@bp.get("/channels")
@authorized()
async def contents(request, userid):
    return response.json(content_table.all())

@bp.get("/channels/<message_id>")
@authorized()
async def getUser(self, userid, message_id):
    query = Query()
    data = content_table.search(query.message.id == message_id)
    if len(data) == 0:
        return response.json({"success": False}}, status=404)
    else:
        return response.json(data[0])

@bp.delete("/channels/<message_id>")
@authorized()
async def delete_content(request, userid, message_id):
    check = content_table.search(content.from_bot == userid)
    if len(check) == 0:
        return response.json({"success": False}, status=401)
    data = content_table.search(content.message.id == message_id)
    if len(data) == 0:
        return response.json({"success": False}, status=404)
    else:
        payload = {
            "type": "delete",
            "data": {
                "from": userid,
                "messageid": message_id
            }
        }
        try:
            await asyncio.gather(*[ws.send(dumper(payload)) for ws in wss])
        except Exception:
            pass
        content_table.remove(content.message.id == message_id)
        return response.json({"success": True}) 
