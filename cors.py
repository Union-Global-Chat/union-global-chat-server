from sanic import Sanic


class CorsExtend:
    def __init__(self, app: Sanic, origin: str="*"):
        self.app = app
        self.origin = origin
        self.app.register_middleware(self.add_cors_header, "response")

        
    async def add_cors_header(self, _, response):
        response.headers["Access-Control-Allow-Origin"] = self.origin
