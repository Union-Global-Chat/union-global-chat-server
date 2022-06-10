from sanic import Sanic
from importlib import import_module
from data import config
import os


app = Sanic("ugc-server")
app.config.CORS_ORIGINS = "*"


for name in os.listdir("blueprints"):
    if name.endswith(".py"):
        lib = import_module("blueprints.{}".format(name[:-3]))
        app.blueprint(lib.bp)
        lib.app = app


app.run(**config)
