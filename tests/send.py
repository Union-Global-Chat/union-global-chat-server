import requests

token = "ik8J6D4qRggWkWBVzti07feetHNh2USP"

def request(method: str, url: str, *args, **kwargs):
    kwargs["headers"] = {"Authorization": "Bearer {}".format(token)}
    return requests.request(method, "http://localhost:8080/api/v2" + url, *args, **kwargs)


def send():
    request("POST", "/channels", json={"test": "test", "message": {"id": 98298392}})
    print(request("GET", "/channels").json())
    print(request("DELETE", "/channels/98298392").json())

send()
