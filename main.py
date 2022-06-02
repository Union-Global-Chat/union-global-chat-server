from tinydb import TinyDB, Query
from sanic import Sanic, response
from importlib import import_module
from orjson import dumps, loads
from data import config
import zlib
import os
import asyncio
from lib import authorized


app = Sanic("ugc-server")

db = TinyDB('db.json')
user = Query()

for name in os.listdir("blueprints"):
    if name.endswith(".py"):
        lib = import_module("blueprints.{}".format(name[:-3]))
        app.blueprint(lib.bp)
        lib.app = app

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

@app.websocket("/api/v0/gateway")
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
            token = db.search(user.token == data["token"])
            if len(token) == 0:
                await ws.send(dumper({"type": "identify", "success": False}))
                await ws.close()
            else:
                await ws.send(dumper({"type": "identify", "success": True}))
                wss.append(ws)
                app.loop.create_task(HeartBeat(ws).sending_heartbeat())

@app.post("/api/v0/channels")
@authorized()
async def send(request, userid):
    payload = {
        "type": "send",
        "data": {
            "from": userid,
            "data": request.json
        }
    }
    for ws in wss:
        await ws.send(dumper(payload))
    return response.json({"success": True})

app.run(**config)