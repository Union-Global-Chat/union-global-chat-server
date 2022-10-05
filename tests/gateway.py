from websockets import connect
import zlib
import asyncio
from orjson import loads

async def main():
    async with connect("ws://localhost:8080/api/v2/gateway") as ws:
        print(loads(zlib.decompress(await ws.recv())))
        await ws.send(zlib.compress(b'{"type": "identify", "data": {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk5MzgyMDk0OTgyIiwidXNlcm5hbWUiOiJ0ZXN0In0.m3kZcDuyMsz-_G87mSKGamnJKAAqkvl8M6eJnuVrD18"}}'))
        while True:
            print(loads(zlib.decompress(await ws.recv())))


asyncio.run(main())