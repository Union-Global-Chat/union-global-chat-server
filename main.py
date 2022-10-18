print("Now running")
from sanic import Sanic, response
from importlib import import_module
from utils import CorsExtend
from data import CONFIG
from aiomysql import create_pool
from httpx import AsyncClient
from asyncio.subprocess import create_subprocess_shell
import os


app = Sanic("ugc-server")
print("Setuping cors")
CorsExtend(app)


for name in os.listdir("blueprints"):
    if not name.startswith("_"):
        print("Loading: {}".format(name))
        lib = import_module("blueprints.{}".format(name.replace(".py", "")))
        app.blueprint(lib.bp)
        lib.app = app
        print("Loaded: {}".format(name))
        
        
@app.before_server_start
async def before(app, loop):
    app.ctx.pool = await create_pool(**CONFIG["mysql"])
    async with AsyncClient() as client:
        await client.post(CONFIG["webhook"], json={"content": "Server is started."})

@app.before_server_stop
async def stop_set(app, _):
    app.ctx.pool.close()
        
@app.get("/")
async def main(request):
    return response.redirect("https://ugc-webpage.vercel.app/")


@app.get("/status")
async def status(request):
    return response.redirect("https://ugc-webpage.vercel.app/status")


@app.get("/support")
async def support(request):
    return response.redirect("https://ugc-webpage.vercel.app/support")

        
@app.post("/git")
async def git(request):
    print("\n".join(i["message"] for i in request.json["commits"]))
    proc = await create_subprocess_shell("sudo -u renorari git pull origin main")
    await proc.wait()
    print("Git pulled")
    print("Now rebooting...")
    app.stop()
    return response.json({"hello": "world"})


app.run(**CONFIG["sanic"])
