# チャンネル

主に送信やメッセージなどを取得するためのやつです。

## GET /api/v1/channels

これを要求すると、データベースに保管されている全てのデータが帰ってきます。

## POST /api/v1/channels

```json
{
    "channel": {
        "name": "text",
        "id": "000000000"
    },
    "author": {
        "username": "name",
        "discriminator": "8888",
        "id": "000000000",
        "avatarURL": "URL(png, dynamic, 512)",
        "bot": false
    },
    "guild": {
        "name": "KGC",
        "id": "000000000",
        "iconURL": "URL(png, dynamic, 256)"
    },
    "message": {
        "content": "",
        "id": "",
        "cleanContent": "メンション等を省いたcontent",
        "?reference": "",
        "?attachments": [{"name": "filename", "url": "fileurl", "?height": "height", "?width": "width", "content_type": "file’s content_type"}],
        "embeds": []
     }
}
```
と送信するとウェブソケットに全部送信されます。

## DELETE: /api/v1/channels/:messageid (未実装)

これを実行することによってデータベースからメッセージを削除し、削除されたことを全botに通知します。
