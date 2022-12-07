import sqlite3
import os
import time

# create database for guild


class DataManager():
    def __init__(self) -> None:
        pass

    def conn(self, guildID: int) -> None:
        if f"{guildID}.db" not in list(os.listdir("./src/data")):
            self.conn = sqlite3.connect(f"./src/data/{guildID}.db")

            # create table
            self.conn.execute("""CREATE TABLE MAIN
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MSGID INT   NOT NULL,
            MESSAGE TEXT    NOT NULL,
            AUTHORID INT    NOT NULL,
            EPOCH INT    NOT NULL,
            CTXID INT)""")
        else:
            self.conn = sqlite3.connect(f"./src/data/{guildID}.db")
        print(f"Connected to Database {guildID}")

    def addData(self, msgID: int, msg: str, authorID: int, ctxID: int = None):
        EPOCH = int(time.time()) * 1000
        if ctxID is not None:
            self.conn.execute(f"""INSERT INTO MAIN (MSGID, MESSAGE, AUTHORID, EPOCH, CTXID)
            VALUES ({msgID}, '{msg}', {authorID}, {EPOCH}, {ctxID})""")

        else:
            self.conn.execute(f"""INSERT INTO MAIN (MSGID, MESSAGE, AUTHORID, EPOCH)
            VALUES ({msgID}, '{msg}', {authorID}, {EPOCH})""")

        self.conn.commit()
