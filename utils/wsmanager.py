from sanic import WebSocket

from typing import List, Any


class WsManager:
    def __init__(self):
        self.protocols: List[WebSocket] = []

    def connect(self, ws: WebSocket) -> None:
        self.protocols.append(ws)

    async def close(self, ws: WebSocket) -> None:
        await ws.close()
        self.protocols.remove(ws)

    async def broadcast(self, content: Any) -> None:
        for protocol in self.protocols:
            await protocol.send(content)
