import discord
from discord.ext import commands
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import (CommandNotFound,CommandOnCooldown,MissingRequiredArgument)

import os
from dotenv import load_dotenv
import sqlite3
import asyncio

from cogs import my_db as db
import cache as ch

PATH = os.path.dirname(os.path.realpath(__file__))


load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

owners = [258080725239201792]
async def is_owner(ctx):
    return ctx.author.id in owners


async def usr_prefix(bot, message):
  main_prefix = ":-"

  if message.author.id in ch.prefix_cache:
    # Using prefix in cache
    return ch.prefix_cache[message.author.id]

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT prefix FROM user WHERE user_id = ?;", (message.author.id,))
    prefix = c.fetchone()
    
  if prefix is not None:
    #generating cache 
    ch.prefix_cache[message.author.id] = prefix[0]
    return prefix[0]
  return main_prefix



class MyBot(commands.Bot):
  async def on_ready(self):      
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f":-help or {bot.user.name}"))
    print('online')
    print("Discord Version:",discord.__version__)
    
  async def on_message(self, message):
    #Show Help | I could use bot.mentioned_in but that would also respond to replies.
    if message.content == f"{bot.user.mention}" or message.content == f"{await usr_prefix(bot, message)}help":
      await help(message)
      
    #Reset prefix
    if bot.user.mentioned_in(message) and message.content == f"{bot.user.mention} ..":
      try:
        await db.insert_user(message.guild.id, message.author.id, 0, 0, 0, 0, 0, ":-", "en")
      except sqlite3.IntegrityError:
        print("usr already in db so i'll be using their data (help)")

      async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
        c.execute("SELECT lang FROM user WHERE user_id = ?;",(message.author.id,))
        lang = c.fetchone()[0]
        
      ch.prefix_cache.update({message.author.id : ":-"})
      await db.update_prefix(message.author.id, ":-") 
      
      if lang != 'es':
        await message.channel.send(f"Now using default prefix `{await usr_prefix(bot, message)}`")
      elif lang == 'en':
        await message.channel.send(f"Ahora usando el prefijo predeterminado `{await usr_prefix(bot, message)}`")


    await bot.process_commands(message)

bot = MyBot(command_prefix=usr_prefix, intents=intents)


class Promobuttons(discord.ui.View):
  
  def __init__(self):
      super().__init__()
    
      url_top = "https://top.gg/bot/800136653041303553/vote"
      url_bot = "https://example.com/"
  
      self.add_item(discord.ui.Button(label='Vote on Top.gg!', url=url_top))
      self.add_item(discord.ui.Button(label='Make your own snipe bot!', url=url_bot))
  




@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound) and ctx.author.id not in owners:
      print("User used prefix with a wrong command")
  elif ctx.author.id in owners:
      print(error)






sniped = {}

@bot.listen()
async def on_message_delete(message):
  sniped[message.channel.id] = [message.content, message.author, message.channel.name, message.attachments, message.created_at]


@bot.command(aliases=['resend', 'snipe', 'recibir'])
async def getmsg(ctx):
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (help)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]
    
  try:        
      contents, author, channel_name, attch, time = sniped[ctx.channel.id]
  except KeyError:
    if lang != 'es':
      return await ctx.channel.send("Nothing to snipe")
    return await ctx.channel.send("Nada que disparar")

    
  sniped_embed = discord.Embed(description=contents, color=discord.Color.blurple(), timestamp=time)
  sniped_embed.set_author(name=f'{author.name}#{author.discriminator}',icon_url=author.display_avatar.url)

  if attch:
    if attch[0].proxy_url.endswith("mp4"):
      await ctx.channel.send(embed=sniped_embed)
      return await ctx.channel.send(content=attch[0].proxy_url)
    else:
      sniped_embed.set_image(url=attch[0].proxy_url)

  if lang != 'es':
    sniped_embed.set_footer(text=f'deleted in {channel_name} ')
    await ctx.channel.send(embed=sniped_embed)
    return await db.update_msg(ctx.author.id)
    
  sniped_embed.set_footer(text=f'eliminado en {channel_name} ')
  await ctx.channel.send(embed=sniped_embed)
  return await db.update_msg(ctx.author.id)





sniped_edit = {}

@bot.listen()
async def on_message_edit(message_before,message_after):
    sniped_edit[message_before.channel.id] = [message_before.content, message_before.author, message_before.channel.name, message_before.created_at]


@bot.command(aliases=['snipeedit', 'recibiredit'])
async def getedit(ctx):
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (help)")

  
  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]
    
  try:
    contents, author, channel_name,time = sniped_edit[ctx.channel.id]
  except KeyError:
    if lang != 'es':
      return await ctx.channel.send("No recently edited message detected")
    return await ctx.channel.send("No hay ningún mensaje editado recientemente")
    
    
  getEdit_embed = discord.Embed(description=contents, color=discord.Color.blurple(), timestamp=time)
  getEdit_embed.set_author(name=f'{author.name}#{author.discriminator}',icon_url=author.display_avatar)

  if lang != 'es':
    getEdit_embed.set_footer(text=f'edited in {channel_name} ')
    await ctx.channel.send(embed=getEdit_embed)
    return await db.update_edit(ctx.author.id)
    
  getEdit_embed.set_footer(text=f'editado en {channel_name} ')
  await ctx.channel.send(embed=getEdit_embed)
  return await db.update_edit(ctx.author.id)
    
















# - - - - - Non Main Features  - - - - - - - #


bot.remove_command('help')



async def help(ctx):
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (help)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT prefix FROM user WHERE user_id = ?;", (ctx.author.id,))
    prefix = c.fetchone()[0]
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]

  if lang == "es":
    es_cog = bot.get_cog("espanol") # Gets the class "espanol" in langs.py
    return await es_cog.sp_help(ctx)

      
  help_Embed = discord.Embed(title='Elite Sniper\'s commands',
  description=f"<:flag_ea:987500016690163782> **Espanol**\n¿Hablas Español? `{prefix}ajustes 2 es`"+
              f"\n---------------\n"+
              f"If you used the correct command and you still don't see the deleted message/image then most likely Discord cleared their cache and the content is gone for good.",
  color=0x459fa5)

  help_Embed.add_field(name='<:white_small_square:987778113599574047> 1. getmsg',value=f'└ The most recently deleted `message` | alias: `snipe`, `resend`',inline=True)
  help_Embed.add_field(name='<:white_small_square:987778113599574047> 2. getedit',value=f'└ The most recently edited `message` | alias: `snipeedit`',inline=True)
  help_Embed.add_field(name='<:white_small_square:987778113599574047> 3. settings',value=f'└ Change your `prefix` | alias: `None`',inline=True)
  #help_Embed.set_footer(text=f"Use {prefix}snreport (message) to report any problems with the bot")

  await ctx.channel.send(embed=help_Embed, view=Promobuttons())
  await db.update_help(ctx.author.id) 





@bot.command(aliases=['ajustes'])
async def settings(ctx, num=0, *, change=None):
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (settings)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:  
    c.execute("SELECT prefix FROM user WHERE user_id = ?;", (ctx.author.id,))
    prefix = c.fetchone()[0]
    c.execute("SELECT lang FROM user WHERE user_id = ?;", (ctx.author.id,))
    lang = c.fetchone()[0]

  if lang == "es":
    es_cog = bot.get_cog("espanol")
    return await es_cog.sp_settings(ctx, num, change)

  if num > 0 and num <=2:
    
    #Change prefix
    if num == 1 and change is not None and len(change) <=3 and len(change) > 0:
      ch.prefix_cache.update({ctx.author.id : change})
      await db.update_prefix(ctx.author.id, change)
      return await ctx.channel.send(f"Prefix changed! You can type \"{bot.user.mention} **..**\" to revert to the default prefix.")
      
    #Change language
    elif num == 2 and change == 'es':
      await db.update_lang(ctx.author.id, change)
      return await ctx.channel.send("✅")
    else:
      if num == 1:
        return await ctx.channel.send("Prefix must be greater than 0 and less than 4.")
      elif num == 2:
        return await ctx.channel.send("I don't have that language or you're already using it.")
      else:
        return await ctx.channel.send("You're not using this command correctly")
    
  settings_em = discord.Embed(title="Settings", description=f"Use `{prefix}settings (settingNum) (input)`. ", color=0x459fa5)
  settings_em.add_field(name="<:white_small_square:987778113599574047> 1. Change Prefix", value=f"└ Change the way you interact with `commands` | eg: `{prefix}settings 1 pls`")
  settings_em.add_field(name="<:white_small_square:987778113599574047> 2. Change Language", value=f"└ Change your current `language` | eg: `{prefix}settings 2 es`")
  settings_em.set_footer(text="Prefix length must be less than 4 characters and greater than 0.")

  await ctx.send(embed=settings_em)













@bot.command()
async def view(ctx, member: discord.Member = None):
  if member is not None:
    async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
      c.execute("SELECT * FROM user WHERE user_id = ?;", (member.id,))
      memberInfo = c.fetchone()
    print(memberInfo)
    return
      
  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT * FROM user;")
    all = c.fetchone()
    print(all)
    return
    



#  - - - - - - LEAVE GUILD - - - - - - -  #



@bot.command()
@commands.check(is_owner)
async def leave(ctx, *, guild_name):

    try:
        guildid = int(guild_name)
    except:
        await ctx.send("Invalid guild: failed to convert to int")
    try:
        guild = bot.get_guild(guildid)
    except:
        await ctx.send("Invalid guild")
    try:
        await guild.leave()
        await ctx.send(f"left {guild.name}")
    except:
        await ctx.send("Error leaving")







# - - - - -   - - - - -  LOAD COGS  - - - - -  - - - - - #

async def main():
  async with bot:  
    for filename in os.listdir('./cogs'):
      if filename != "my_db.py" and filename.endswith('.py'):
        await bot.load_extension(f'cogs.{filename[:-3]}')
    await db.c_table()
    await bot.start(TOKEN)


asyncio.run(main())
