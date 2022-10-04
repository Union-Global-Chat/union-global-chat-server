from sanic import WebSocket

import asyncio


class HeartBeat:
    def __init__(self, ws):
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
