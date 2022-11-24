from contextlib import asynccontextmanager
import os
import sqlite3

PATH = os.path.dirname(os.path.realpath(__file__))


@asynccontextmanager
async def get_db(db_name):
  conn = sqlite3.connect(db_name)
  yield conn.cursor()
  conn.commit()
  conn.close()




async def c_table():
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("""CREATE TABLE IF NOT EXISTS user (
        server_id INT,
        user_id INT,
        getmsg INT,
        getedit INT,
        help INT,
        topgg INT,
        bots INT,
        access INT,
        prefix VARCHAR(3),
        lang VARCHAR(2),
        PRIMARY KEY(user_id)
    ) """)


async def c_embed():
  async with get_db(f"{PATH}/data/embed.db") as c:
    c.execute("""CREATE TABLE IF NOT EXISTS embed (
        server_id JSON DEFAULT('[]'),
        channel_id JSON DEFAULT('[]'),
        msg_id JSON DEFAULT('[]'),
        user_id INT,
        PRIMARY KEY(user_id)
    ) """)


async def delete_embed(usr_id):
  async with get_db(f"{PATH}/data/embed.db") as c:
    c.execute("DELETE FROM embed WHERE user_id = ?", (usr_id,))




async def insert_embed(user_id):
  async with get_db(f"{PATH}/data/embed.db") as c:
    c.execute("INSERT INTO embed(user_id) VALUES (?)",
            (user_id,))



async def update_embed(server_id, channel_id, msg_id, usr_id):
  async with get_db(f"{PATH}/data/embed.db") as c: #No SQL Injection? 🥺
    c.execute(f"UPDATE embed SET server_id = json_insert(server_id, '$[#]', {server_id}) WHERE user_id = {usr_id};")
    c.execute(f"UPDATE embed SET channel_id = json_insert(channel_id, '$[#]',{channel_id}) WHERE user_id = {usr_id};")
    c.execute(f"UPDATE embed SET msg_id = json_insert(msg_id, '$[#]', {msg_id}) WHERE user_id = {usr_id};")




async def insert_user(server_id, user_id, getmsg, getedit, help, topgg, bots, access, prefix=":-", lang="en"):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (server_id, user_id, getmsg, getedit, help, topgg, bots, access, prefix, lang,))








async def update_msg(usr_name):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET getmsg = getmsg + 1  WHERE user_id = ?;", (usr_name,))
    
async def update_edit(usr_name):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET getedit = getedit  + 1  WHERE user_id = ?;", (usr_name,))


async def update_help(usr_name):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET help = help + 1  WHERE user_id = ?;", (usr_name,))

async def update_access(usr_name, mode):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET access = ? WHERE user_id = ?;", (mode, usr_name,))

async def update_prefix(usr_name, prefix):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET prefix = ? WHERE user_id = ?;", (prefix, usr_name,))

async def update_lang(usr_name, lang):
  async with get_db(f"{PATH}/data/users.db") as c:
    c.execute("UPDATE user SET lang = ? WHERE user_id = ?;", (lang, usr_name,))
