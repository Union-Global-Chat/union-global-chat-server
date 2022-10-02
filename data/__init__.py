from toml import load

from typing import TypedDict


class ConfigSanicType(TypedDict):
    host: str
    port: str

class ConfigType(TypedDict):
    webhook: str
    sanic: ConfigSanicType
    mysql: dict

with open("config.toml", "r") as f:
    CONFIG: ConfigType = load(f)
