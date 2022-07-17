from contextlib import asynccontextmanager
import os
import sqlite3

PATH = os.path.dirname(os.path.realpath(__file__))


@asynccontextmanager
async def get_db(db_name):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  yield c
  conn.commit()
  conn.close()




async def c_table():
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("""CREATE TABLE user (
        server_id INT,
        user_id INT,
        getmsg INT,
        getedit INT,
        help INT,
        topgg BIT,
        bots BIT,
        access INT,
        prefix VARCHAR(3),
        lang VARCHAR(2),
        PRIMARY KEY(user_id)
    ) """)


async def insert_user(server_id, user_id, getmsg, getedit, help, topgg, bots, access, prefix=":-", lang="en"):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (server_id, user_id, getmsg, getedit, help, topgg, bots, access, prefix, lang,))



async def update_msg(usr_name):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute(f"UPDATE user SET getmsg = getmsg + 1  WHERE user_id = ?;", (usr_name,))
    
async def update_edit(usr_name):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute(f"UPDATE user SET getedit = getedit  + 1  WHERE user_id = ?;", (usr_name,))


async def update_help(usr_name):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute(f"UPDATE user SET help = help + 1  WHERE user_id = ?;", (usr_name,))

async def update_access(usr_name, mode):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET access = ? WHERE user_id = ?;", (mode, usr_name,))

async def update_prefix(usr_name, prefix):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET prefix = ? WHERE user_id = ?;", (prefix, usr_name,))

async def update_lang(usr_name, lang):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET lang = ? WHERE user_id = ?;", (lang, usr_name,))

