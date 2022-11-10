from data import CONFIG
from argparse import ArgumentParser

import jwt
import pymysql


def main(bot_id, bot_name):
    connection = pymysql.connect(**CONFIG["mysql"])
    with connection:
        with connection.cursor() as cur:
            cur.execute(
                "INSERT INTO User VALUES(%s, %s);",
                (bot_id, bot_name)
            )
    print(jwt.encode({"id": bot_id, "username": bot_name}, CONFIG["secret_key"]))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--id", help="Bot's id")
    parser.add_argument("--name", help="Bot's name")
    args = parser.parse_args()
    if not args.id:
        bot_id = input("Bot's Id: ")
    else:
        bot_id = args.id
    if not args.name:
        bot_name = input("Bot's Name: ")
    else:
        bot_name = args.name
    main(bot_id, bot_name)
