from sanic import Sanic, response
from importlib import import_module
from cors import CorsExtend
from data import config
import subprocess
import os


app = Sanic("ugc-server")
CorsExtend(app)


for name in os.listdir("blueprints"):
    if name.endswith(".py"):
        lib = import_module("blueprints.{}".format(name[:-3]))
        app.blueprint(lib.bp)
        lib.app = app
        
        
@app.get("/")
async def main(request):
    return response.redirect("https://ugc-webpage.vercel.app/")

        
@app.post("/git")
async def git(request):
    print("updating...")
    subprocess.run(["git", "pull", "origin", "main"])
    app.stop()
    return response.json({"hello", "world"})


app.run(**config)
