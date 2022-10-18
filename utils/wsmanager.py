from sanic import Websocket

from typing import List, Any


class WsManager:
    def __init__(self):
        self.protocols: List[Websocket] = []

    def connect(self, ws: Websocket) -> None:
        self.protocols.append(ws)

    async def close(self, ws: Websocket) -> None:
        await ws.close()
        self.protocols.remove(ws)

    async def broadcast(self, content: Any) -> None:
        for protocol in self.protocols:
            try:
                await protocol.send(content)
            except Exception:
                self.protocols.remove(protocol)
