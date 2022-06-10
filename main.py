from sanic import Sanic, response
from importlib import import_module
from data import config
import subprocess
import os


app = Sanic("ugc-server")
app.config.CORS_ORIGINS = "*"


for name in os.listdir("blueprints"):
    if name.endswith(".py"):
        lib = import_module("blueprints.{}".format(name[:-3]))
        app.blueprint(lib.bp)
        lib.app = app
        
@app.post("/git")
async def git(request):
    subprocess.run(["git", "pull", "origin", "main"])
    return response.json({"hello", "world"})


app.run(**config)
