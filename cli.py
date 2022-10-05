from data import CONFIG

import jwt
from pymysql


def main():
    connection = pymysql.connect(**CONFIG["mysql"])
    bot_id, bot_name = input("Bot's Id: "), input("Bot's Name: ")
    with connection:
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO User VALUES(%s, %s);",
                (bot_id, bot_name)
            )
    print(jwt.encode({"id": bot_id, "username": bot_name}, CONFIG["secret"]))

if __name__ == "__main__":
    main()
