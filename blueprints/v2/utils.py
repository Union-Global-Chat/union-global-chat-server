from sanic import Websocket
import jwt
from jwt.exceptions import InvalidSignatureError
from orjson import dumps

import asyncio
from functools import wraps
from time import time
import zlib

from data import CONFIG



def dumper(type: str, data: dict=None, *, success: bool=True, message: str=None, code: int=200):
    payload = {
        "type": type,
        "data": data,
        "code": code,
        "success": success,
        "message": message
    }
    return zlib.compress(dumps(payload))


def authorized(func):
    @wraps(func)
    async def decorated_func(request, *args, **kwargs):
        try:
            user = jwt.decode(request.token, CONFIG["secret_key"], algorithms=["HS256"])
        except InvalidSignatureError:
            return json(message="Authorized failed", status=401)
        else:
            return await func(request, user, *args, **kwargs)
    return decorated_func
        

class HeartBeat:
    def __init__(self, ws: Websocket, queue: asyncio.Queue, client_id: str):
        self.ws = ws
        self.open: bool = True
        self.queue = queue
        self.client_id = client_id

    async def send_heartbeat(self):
        await self.ws.send(dumper('heartbeat', {"unix_time": time()}))

    async def start(self):
        while self.open:
            try:
                payload = await asyncio.wait_for(self.queue.get(), timeout=30)
                if payload["type"] == "heartbeat":
                    await self.send_heartbeat()
                    await asyncio.sleep(10)
            except asyncio.TimeoutError:
                self.open = False
