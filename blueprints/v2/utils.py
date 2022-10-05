from sanic import Websocket
import jwt
from jwt.exceptions import InvalidSignatureError

import asyncio
from functools import wraps

from data import CONFIG


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
    def __init__(self, ws: Websocket):
        self.ws = ws
        self.open: bool = True

    async def send_heartbeat(self):
        await self.ws.send(dumper('heartbeat', {"unix_time": time()}))

    async def start(self):
        while self.open:
            try:
                payload = loads(zlib.decompress(await asyncio.wait_for(self.ws.recv(), timeout=30)))
                if payload["type"] == "heartbeat":
                    await self.send_heartbeat()
                    await asyncio.sleep(10)
            except asyncio.TimeoutError:
                await manager.disconnect(ws)
                self.open = False
