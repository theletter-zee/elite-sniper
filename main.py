import discord
from discord.ext import commands
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import (CommandNotFound,CommandOnCooldown,MissingRequiredArgument)

import os
from dotenv import load_dotenv
import sqlite3
import asyncio
import json

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f":-help or @{bot.user.name}"))
    print('online')
    print("Discord Version:",discord.__version__)
    
  async def on_message(self, message):
    #Show Help | I could use bot.mentioned_in but that would also respond to replies.
    if message.content == f"{bot.user.mention}" or message.content == f"{await usr_prefix(bot, message)}help":
      await help(message)
      
    #Reset prefix
    if bot.user.mentioned_in(message) and message.content == f"{bot.user.mention} ..":
      try:
        await db.insert_user(message.guild.id, message.author.id, 0, 0, 0, 0, 0, 1, ":-", "en")
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
      url_bot = "https://example.com/" #Incoming youtube tutorial :)
  
      self.add_item(discord.ui.Button(label='Vote on Top.gg!', url=url_top))
      self.add_item(discord.ui.Button(label='Make your own snipe bot!', url=url_bot))
  




@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound) and ctx.author.id not in owners:
      print("User used prefix with a wrong command")
  elif ctx.author.id in owners:
      print(error)






sniped = {}
sniped_edit = {}



@bot.listen()
async def on_message_delete(message):
  sniped[message.channel.id] = [message.content, message.author, message.channel.name, message.attachments, message.created_at]
  



@bot.listen()
async def on_message_edit(message_before, message_after):
    sniped_edit[message_before.channel.id] = [message_before.content, message_before.author, message_before.channel.name, message_before.created_at]





@bot.command(aliases=['resend', 'snipe', 'recibir'])
async def getmsg(ctx):
  #Checks if the person snipiping is in the db
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (getmsg)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]

  try:        
      contents, target, channel_name, attch, time = sniped[ctx.channel.id]
  except KeyError:
    if lang != 'es':
      return await ctx.channel.send("Nothing to snipe")
    return await ctx.channel.send("Nada que disparar")

  #Checks if the person getting sniped is in the db
  try:
    await db.insert_user(ctx.guild.id, target.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("target already in db so i'll be using their data (getmsg)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT access FROM user WHERE user_id = ?;",(target.id,))
    access_target = c.fetchone()[0]
    c.execute("SELECT access FROM user WHERE user_id = ?;",(ctx.author.id,))
    access_author = c.fetchone()[0]


  # Checks if the user has sniping enabled.
  # This could be 1 statement w/ an "or" operator but I want it to be more specific.
  if access_target == 0:
    if lang != 'es':
      return await ctx.channel.send("The target has disabled sniping in their `settings`")
    return await ctx.channel.send("El objetivo ha deshabilitado el francotirador en su `configuración`")
  elif access_author == 0:
    if lang != 'es':
      return await ctx.channel.send("You have disabled sniping in your `settings`")
    return await ctx.channel.send("Has deshabilitado el francotirador en la `configuración`")
  

    
  sniped_embed = discord.Embed(description=contents, color=discord.Color.blurple(), timestamp=time)
  sniped_embed.set_author(name=f'{target}',icon_url=target.display_avatar.url)

  if attch:
    if attch[0].proxy_url.endswith("mp4"):
      await ctx.channel.send(embed=sniped_embed)
      msg = await ctx.channel.send(content=attch[0].proxy_url)

      # Save message id so user can terminate their snipes
      try:
        return await db.insert_embed(target.id, msg.id)
      except:
        print("\n\nTarget dictionary already in db. Updating message id in dictionary")

      return await db.update_embed(target.id, msg.id)


    else:
      sniped_embed.set_image(url=attch[0].proxy_url)


  sniped_embed.set_footer(text=f'{channel_name} ')
  msg = await ctx.channel.send(embed=sniped_embed)
  # Save message id & channel id so user can terminate their sniped msgs
  await db.embed_check(target.id, ctx.channel.id)
  await db.read_db()
  try:
    await db.update_db(target.id, ctx.channel.id, msg.id)
  except KeyError:
    await db.add_chan(ctx.author.id, ctx.channel.id)
    await db.update_db(target.id, ctx.channel.id, msg.id)


  await db.update_msg(ctx.author.id)










@bot.command(aliases=['snipeedit', 'recibiredit'])
async def getedit(ctx):
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (getedit)")

  
  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]
    
  try:
    contents, target, channel_name, time = sniped_edit[ctx.channel.id]
  except KeyError:
    if lang != 'es':
      return await ctx.channel.send("No recently edited message detected")
    return await ctx.channel.send("No hay ningún mensaje editado recientemente")


  try:
    await db.insert_user(ctx.guild.id, target.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("target already in db so i'll be using their data (getmsg)")


  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT access FROM user WHERE user_id = ?;",(target.id,))
    access_target = c.fetchone()[0]
    c.execute("SELECT access FROM user WHERE user_id = ?;",(ctx.author.id,))
    access_author = c.fetchone()[0]

    
  if access_target == 0:
    if lang != 'es':
      return await ctx.channel.send("The target has disabled sniping in their `settings`")
    return await ctx.channel.send("El objetivo ha deshabilitado el francotirador en su `configuración`")
  elif access_author == 0:
    if lang != 'es':
      return await ctx.channel.send("You have disabled sniping in your `settings`")
    return await ctx.channel.send("Has deshabilitado el francotirador en la `configuración`")
    
  getEdit_embed = discord.Embed(description=contents, color=discord.Color.blurple(), timestamp=time)
  getEdit_embed.set_author(name=f'{target}',icon_url=target.display_avatar)

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
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
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
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (settings)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:  
    c.execute("SELECT prefix FROM user WHERE user_id = ?;", (ctx.author.id,))
    prefix = c.fetchone()[0]
    c.execute("SELECT lang FROM user WHERE user_id = ?;", (ctx.author.id,))
    lang = c.fetchone()[0]
    c.execute("SELECT access FROM user WHERE user_id = ?;", (ctx.author.id,))
    access_author = c.fetchone()[0]

  if lang == "es":
    es_cog = bot.get_cog("espanol")
    return await es_cog.sp_settings(ctx, num, change)


  if num > 0 and num <=3:
    
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
  if access_author == 0:
    #Snipe is disabled - show X
    settings_em.add_field(name="<:white_small_square:987778113599574047> 3. Usage", value=f"└ If disabled, your messages cannot be sniped and you cannot snipe other messages as well. | eg: `{prefix}usage on` | Currently: **DISABLED**")
  
  settings_em.add_field(name="<:white_small_square:987778113599574047> 3. Usage", value=f"└ If disabled, your messages will not be sniped and you cannot snipe other messages as well. | eg: `{prefix}usage off` | Currently: **ENABLED**")
  settings_em.set_footer(text="Prefix length must be less than 4 characters and greater than 0.")

  await ctx.send(embed=settings_em)






@bot.command(aliases=['uso'])
async def usage(ctx, *, mode):
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (help)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT access FROM user WHERE user_id = ?;", (ctx.author.id,))
    access_author = c.fetchone()[0]
    c.execute("SELECT lang FROM user WHERE user_id = ?;", (ctx.author.id,))
    lang = c.fetchone()[0]

  if lang == "es":
    es_cog = bot.get_cog("espanol")
    return await es_cog.sp_usage(ctx, mode)

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) == '👍'

  if mode == "off":
    if access_author == 0:
      return await ctx.channel.send("You already have this disabled.")

    msg = await ctx.channel.send("**Are you sure?** All your messages that has been sniped by other people will be deleted and you will no longer be able to snipe or get sniped (You can turn this back on if you change your mind). React to confirm. (Your messages are fine, only the sniped embeds will be deleted)")
    await msg.add_reaction('👍')

    try:
      reaction, user = await bot.wait_for('reaction_add', timeout=35, check=check)
    except asyncio.TimeoutError:
      await ctx.channel.send("You didn't react in time.")
    else:
      embeds = await db.read_db()
      try:
        for chan in embeds[str(ctx.author.id)]:
          channel = bot.get_channel(int(chan))
          
          for msg_id in embeds[str(ctx.author.id)][str(chan)]['msg_id']:
            msg = await channel.fetch_message(msg_id)
            await msg.delete()
      except:
        print("\n\n Original Embed was deleted, skipping ")

      embeds.pop(str(ctx.author.id))
      with open(PATH+"/cogs/data/embed.json", 'w') as f:
        json.dump(embeds, f, indent=2)
        

      await db.update_access(ctx.author.id, 0)
      return await ctx.channel.send("You will no longer have your messages sniped & You can no longer snipe messages.  (You can still enable it again)")
  elif mode == 'on':
    if access_author == 1:
      return await ctx.channel.send("You already have this enabled.")

    await db.update_access(ctx.author.id, 1)
    return await ctx.channel.send("You can now snipe deleted messages!")
  else:
    await ctx.channel.send("Check settings for more info on how to use this command.")

    





    



#  - - - - - - LEAVE GUILD - - - - - - -  #


@bot.command()
@commands.check(is_owner)
async def leave(ctx):
  await ctx.guild.leave()




# - - - - -   - - - - -  LOAD COGS  - - - - -  - - - - - #

async def main():
  async with bot:  
    for filename in os.listdir('./cogs'):
      if filename != "my_db.py" and filename.endswith('.py'):
        await bot.load_extension(f'cogs.{filename[:-3]}')
    await db.c_table()
    await bot.start(TOKEN)


asyncio.run(main())
