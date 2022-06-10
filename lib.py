from functools import wraps
from tinydb import TinyDB, Query
from sanic import response

db = TinyDB('db.json')
table = db.table("token")
user = Query()

def json(data: dict=None, *, message: str=None,
         status: int=200):
    success = True
    if status != 200:
        success = False
    return response.json({"success": success, "status": status, "message": message, "data": data})

def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            s = table.search(user.token == request.token)
            if len(s) == 0:
                return json(message="Authorized failed", status=401)
            else:
                return await f(request, s[0]["user"], *args, **kwargs)
        return decorated_function
    return decorator

def loop(seconds: int):
    pass
