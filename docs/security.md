# 認証

## 方式

主にヘッダーを用いて認証します。

事前に管理者からトークンが渡されるのでそれで認証してください。

| 名前 | 値 |
| ---- | ---- |
| Authorization | Bearer {token} |

## 例

### Python
```python
import requests


token = ""

requests.get("https://ugc.renorari.net/api/v1/channels", headers={
    "Authorization": f"Bearer {token}"
})
```

### JavaScript

```javascript
const token = "";

fetch("https://ugc.renorari.net/api/v1/channels", {
    "method": "GET",
    "headers": {
        "Authorization": `Bearer ${token}`
    }
});
```
