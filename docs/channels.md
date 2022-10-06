# チャンネル

主に送信やメッセージなどを取得するためのやつです。

## GET /api/v1/channels

これを要求すると、データベースに保管されている全てのデータが帰ってきます。

## GET /api/v1/channels/:messageid

データベースからメッセージIDを検索し、あるならデータが返ってきます。

## POST /api/v1/channels

送信すると接続しているすべてのウェブソケットに送信されます。

### JSON data

| name    | type                             |
| ---     | ---                              |
| channel | [Channel object](types/channel) |
| author  | [Author object](types/author)   |
| guild   | [Guild object](types/guild)     |
| message | [Message object](types/message) |

## DELETE: /api/v1/channels/:messageid (Beta)

これを実行することによってデータベースからメッセージを削除し、削除されたことを全botに通知します。
