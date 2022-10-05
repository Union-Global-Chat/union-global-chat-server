import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk5MzgyMDk0OTgyIiwidXNlcm5hbWUiOiJ0ZXN0In0.m3kZcDuyMsz-_G87mSKGamnJKAAqkvl8M6eJnuVrD18"

def request(method: str, url: str, *args, **kwargs):
    kwargs["headers"] = {"Authorization": "Bearer {}".format(token)}
    return requests.request(method, "http://localhost:8080/api/v2" + url, *args, **kwargs)


def send():
    request("POST", "/messages", json={
        "author": {
            "id": "99382094982",
            "username": "test",
            "discriminator": "0000",
            "avatarURL": None,
            "bot": False
        },
        "channel": {
            "id": "99382094982",
            "name": "test"
        },
        "guild": {
            "name": "test",
            "id": "99382094982",
            "iconURL": None
        },
        "message": {
            "id": "99382094982",
            "content": "test",
            "attachments": [],
            "clean_content": "test",
            "embeds": []
        }
    })

send()
