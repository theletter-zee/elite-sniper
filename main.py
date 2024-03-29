#pip install -U git+https://github.com/Rapptz/discord.py

from webserver import keep_alive
import discord
from discord.ext import commands
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import (CommandNotFound,CommandOnCooldown,MissingRequiredArgument)


import os
import sqlite3
import asyncio

from cogs import my_db as db
from dotenv import load_dotenv


PATH = os.path.dirname(os.path.realpath(__file__))
os.chdir(PATH)

load_dotenv()



TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

owners = [258080725239201792]
async def is_owner(ctx):
    return ctx.author.id in owners

prefix_cache = {}
async def usr_prefix(bot, message):
  main_prefix = ":-"

  if message.author.id in prefix_cache:
    # Using prefix in cache
    return prefix_cache[message.author.id]

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT prefix FROM user WHERE user_id = ?;", (message.author.id,))
    prefix = c.fetchone()
    
  if prefix is not None:
    #generating cache 
    prefix_cache[message.author.id] = prefix[0]
    return prefix[0]
  return main_prefix



class MyBot(commands.Bot):
  async def on_ready(self):
    print('online')
    print("Discord Version:",discord.__version__)
    
  async def on_message(self, message):
    #Show Help | I could use bot.mentioned_in but that would also respond to replies.
    if message.content == f"{bot.user.mention}":
      await help(message)
      
    #Reset prefix
    if bot.user.mentioned_in(message) and message.content == f"{bot.user.mention} ..":
      try:
        await db.insert_user(message.guild.id, message.author.id, 0, 0, 0, 0, 0, 1, ":-", "en")
      except sqlite3.IntegrityError:
        print("usr already in db so i'll be using their data (reset prefix)")

      async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
        c.execute("SELECT lang FROM user WHERE user_id = ?;",(message.author.id,))
        lang = c.fetchone()[0]
        c.execute("SELECT prefix FROM user WHERE user_id = ?;",(message.author.id,))
        prefix = c.fetchone()[0]

      lang_cog = bot.get_cog('espanol')

      if prefix == ':-':
        return await message.channel.send(await lang_cog.message_trans(lang=lang, section='alreadyPrefix'))
        
      prefix_cache.update({message.author.id : ":-"})
      await db.update_prefix(message.author.id, ":-") 
      
      await message.channel.send(await lang_cog.message_trans(lang=lang, section='nowDefault') + f"{await usr_prefix(bot, message)}`")


    await bot.process_commands(message)

bot = MyBot(command_prefix=usr_prefix, intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name=f":-help or @Elite Sniper"))



class Promobuttons(discord.ui.View):
  
  def __init__(self):
      super().__init__()
    
      #url_top = "https://top.gg/bot/800136653041303553/vote"
      url_bot = "https://github.com/theletter-zee/snipe-bot/tree/master" 
  
      #self.add_item(discord.ui.Button(label='Vote on Top.gg!', url=url_top))
      self.add_item(discord.ui.Button(label='Make Your Own!', url=url_bot))
  




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
  sniped[message.channel.id] = [message.content, message.author, message.channel.name, message.attachments, message.stickers, message.created_at]
  



@bot.listen()
async def on_message_edit(message_before, message_after):
    sniped_edit[message_before.channel.id] = [message_before.content, message_before.author, message_after.content, message_before.channel.name, message_before.created_at]





@bot.hybrid_command(aliases=['resend', 'snipe', 'recibir'])
async def getmsg(ctx):
  """Send the most recently deleted message!"""

  #Checks if the person snipiping is in the db
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (getmsg)")


  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]

  try:
    contents, target, channel_name, attch, stickers, time = sniped[ctx.channel.id]
  except KeyError:
    return await ctx.send(await bot.get_cog("espanol").getmsg_trans(lang=lang, section='error'))


  #Checks if the person getting sniped is in the db
  try:
    await db.insert_user(ctx.guild.id, target.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("target already in db so i'll be using their data (getmsg)")

  #Checks if the person getting sniped is in the embed db
  try:
    await db.insert_embed(target.id)
  except sqlite3.IntegrityError:
    print("usr already in embed db so i'll be using their data (getmsg)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT access FROM user WHERE user_id = ?;",(target.id,))
    access_target = c.fetchone()[0]
    c.execute("SELECT access FROM user WHERE user_id = ?;",(ctx.author.id,))
    access_author = c.fetchone()[0]


  # Checks if the user/target has sniping enabled.
  if access_target == 0:
    return await ctx.send(await bot.get_cog("espanol").getmsg_trans(lang=lang, section='access_target'))
  elif access_author == 0:
    return await ctx.send(await bot.get_cog("espanol").getmsg_trans(lang=lang, section='access_author'))
  
    
  sniped_embed = discord.Embed(description=contents, color=discord.Color.blurple(), timestamp=time)
  sniped_embed.set_author(name=f'{target}',icon_url=target.display_avatar.url)

  if attch:
    if attch[0].proxy_url.endswith("mp4"):
      await ctx.send(embed=sniped_embed)
      msg = await ctx.send(content=attch[0].proxy_url)

      # Save message id if target wishes to terminate their sniped msgs
      return await db.update_embed(ctx.guild.id, ctx.channel.id, msg.id, target.id)

    else:
      sniped_embed.set_image(url=attch[0].proxy_url)
        
  if stickers:
    for sticker in stickers:
      sniped_embed.set_image(url=sticker.url)

  sniped_embed.set_footer(text=f'{channel_name} ')
  msg = await ctx.send(embed=sniped_embed)

  await db.update_embed(ctx.guild.id, ctx.channel.id, msg.id, target.id)

  await db.update_msg(ctx.author.id)










@bot.hybrid_command(aliases=['snipeedit', 'recibiredit'])
async def getedit(ctx):
  """Send the most recently edited message"""
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (getedit)")
    

  
  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT lang FROM user WHERE user_id = ?;",(ctx.author.id,))
    lang = c.fetchone()[0]

  lang_cog = bot.get_cog('espanol')
    
  try:
    original, target, edited, channel_name, time = sniped_edit[ctx.channel.id]
  except KeyError as e:
    return await ctx.send(await lang_cog.getedit_trans(lang=lang, section='error'))


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
    return await ctx.send(await lang_cog.getedit_trans(lang=lang, section='access_target'))
  elif access_author == 0:
    return await ctx.send(await lang_cog.getedit_trans(lang=lang, section='access_author'))

  embed = discord.Embed(color=discord.Color.blurple(), timestamp=time)
  embed.set_author(name=target.name, icon_url=target.display_avatar.url)

  embed.add_field(name="Edited to", value=edited, inline=False)
  embed.add_field(name="Original", value=original, inline=False)
  embed.set_footer(text=f'{channel_name}')
  await ctx.send(embed=embed)
  return await db.update_edit(ctx.author.id)

    
















# - - - - - Non Main Features  - - - - - - - #


bot.remove_command('help')



@bot.hybrid_command()
async def help(ctx):
  """Clarification on how commands work"""
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (help)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:    
    c.execute("SELECT prefix FROM user WHERE user_id = ?;", (ctx.author.id,))
    prefix = c.fetchone()[0]
    c.execute("SELECT lang FROM user WHERE user_id = ?;", (ctx.author.id,))
    lang = c.fetchone()[0]

  lang_cog = bot.get_cog('espanol')

  help_Embed = discord.Embed(title=await lang_cog.help_trans(lang=lang, section='title'),
  description=await lang_cog.help_trans(lang=lang, section='desc_a') + f"`{prefix}{await lang_cog.help_trans(lang=lang, section='ch_lang')}`"+
              f"\n---------------\n"+
              await lang_cog.help_trans(lang=lang, section='desc_b'),
  color=0x459fa5)


  help_Embed.add_field(name=await lang_cog.help_trans(lang=lang, section='getmsg_name'), value=await lang_cog.help_trans(lang=lang, section='getmsg_value'), inline=True)
  help_Embed.add_field(name=await lang_cog.help_trans(lang=lang, section='getedit_name'), value=await lang_cog.help_trans(lang=lang, section='getedit_value'), inline=True)
  help_Embed.add_field(name=await lang_cog.help_trans(lang=lang, section='settings_name'), value=await lang_cog.help_trans(lang=lang, section='settings_value'), inline=True)
 
  await ctx.send(embed=help_Embed, view=Promobuttons()) #.channel is needed or else it wont send
  await db.update_help(ctx.author.id) 





@bot.hybrid_command(aliases=['ajustes'])
async def settings(ctx, num=0, *, change=None):
  """Modify the way you interact with the bot"""
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

  lang_cog = bot.get_cog('espanol')

  if num > 0 and num <=3:
    
    #Change prefix
    if num == 1 and change is not None and len(change) <=3 and len(change) > 0:
      prefix_cache.update({ctx.author.id : change})
      await db.update_prefix(ctx.author.id, change)
      return await ctx.send(await lang_cog.settings_trans(lang=lang, section='changePrefix_A') + f"\"{bot.user.mention} **..**\"" + await lang_cog.settings_trans(lang=lang, section='changePrefix_B') )
      
    #Change language
    elif num == 2 and change == 'es':
      await db.update_lang(ctx.author.id, change)
      return await ctx.send("✅")

    elif num == 2 and change == 'en':
      await db.update_lang(ctx.author.id, change)
      return await ctx.send("✅")

    else:
      if num == 1:
        return await ctx.channel.send(await lang_cog.settings_trans(lang=lang, section='numError_1'))
      elif num == 2:
        return await ctx.channel.send(await lang_cog.settings_trans(lang=lang, section='numError_2'))
      else:
        return await ctx.channel.send(await lang_cog.settings_trans(lang=lang, section='otherError'))
    
  settings_em = discord.Embed(title=await lang_cog.settings_trans(lang=lang, section='title'), description=await lang_cog.settings_trans(lang=lang, section='desc_a') + f"{prefix}" + await lang_cog.settings_trans(lang=lang, section='desc_b'), color=0x459fa5)
  settings_em.add_field(name=await lang_cog.settings_trans(lang=lang, section='changePrefix_name'), value=await lang_cog.settings_trans(lang=lang, section='changePrefix_value_a') + f"{prefix}" + await lang_cog.settings_trans(lang=lang, section='changePrefix_value_b'))
  settings_em.add_field(name=await lang_cog.settings_trans(lang=lang, section='changeLang_name'), value=await lang_cog.settings_trans(lang=lang, section='changeLang_value_a') + f"{prefix}" + await lang_cog.settings_trans(lang=lang, section='changeLang_value_b'))
  
  if access_author == 0:
    #Snipe is disabled - show X
    settings_em.add_field(name=await lang_cog.settings_trans(lang=lang, section='usageName'), value=await lang_cog.settings_trans(lang=lang, section='usageValue_a') + f"{prefix}" + await lang_cog.settings_trans(lang=lang, section='usageDisabled_value_b'))
    settings_em.set_footer(text=await lang_cog.settings_trans(lang=lang, section='numError_1'))
    return await ctx.send(embed=settings_em)
  else:
    settings_em.add_field(name=await lang_cog.settings_trans(lang=lang, section='usageName'), value=await lang_cog.settings_trans(lang=lang, section='usageValue_a') + f"{prefix}" + await lang_cog.settings_trans(lang=lang, section='usageEnabled_value_a'))
    settings_em.set_footer(text=await lang_cog.settings_trans(lang=lang, section='numError_1'))

    await ctx.send(embed=settings_em)





@bot.hybrid_command(aliases=['usar'])
@cooldown(1,86400,BucketType.user)
async def usage(ctx, *, mode):
  """If disabled, your messages cannot be sniped"""
  try:
    await db.insert_user(ctx.guild.id, ctx.author.id, 0, 0, 0, 0, 0, 1, prefix=":-", lang="en")
  except sqlite3.IntegrityError:
    print("usr already in db so i'll be using their data (usage)")

  async with db.get_db(f"{PATH}/cogs/data/users.db") as c:
    c.execute("SELECT access FROM user WHERE user_id = ?;", (ctx.author.id,))
    access_author = c.fetchone()[0]
    c.execute("SELECT lang FROM user WHERE user_id = ?;", (ctx.author.id,))
    lang = c.fetchone()[0]

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) == '👍'

  lang_cog = bot.get_cog('espanol')

  if mode == "off":
    if access_author == 0:
      return await ctx.send(await lang_cog.usage_trans(lang=lang, section='alreadyDisabled'))

    msg = await ctx.send(await lang_cog.usage_trans(lang=lang, section='modeConfirm'))
    await msg.add_reaction('👍')


    try:
      reaction, user = await bot.wait_for('reaction_add', timeout=35, check=check)
    except asyncio.TimeoutError:
      await ctx.send(await lang_cog.usage_trans(lang=lang, section='reactError'))
    else:
      await db.update_access(ctx.author.id, 0)
      return await ctx.reply(await lang_cog.usage_trans(lang=lang, section='usageOff'))
  elif mode == 'on':
    if access_author == 1:
      return await ctx.send(await lang_cog.usage_trans(lang=lang, section='alreadyDisabled'))

    await db.update_access(ctx.author.id, 1)
    return await ctx.send(await lang_cog.usage_trans(lang=lang, section='enabled'))
  else:
    await ctx.send(await lang_cog.usage_trans(lang=lang, section='checkSettings'))






@usage.error
async def tasks_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown_embed = discord.Embed(title='Slow Down!',description='You have to wait **{:.2f}**s  to use this command again.'.format(error.retry_after))
        await ctx.send(embed=cooldown_embed)
    else:
        raise error





@bot.hybrid_command()
async def bing(ctx):
  """Mr. Trump!?"""
  await ctx.send("bong!")




#  - - - - - - LEAVE GUILD - - - - - - -  #


@bot.command()
@commands.check(is_owner)
async def leave(ctx):
  await ctx.guild.leave()




  


from typing import Optional
from typing import Literal
from discord.ext.commands import Greedy

#  - - - - - -  Sync command (by Umbra) - - - - - - -  #
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None):
    """
    :-sync -> global sync
    :-sync ~ -> sync current guild
    :-sync * -> copies all global app commands to current guild and syncs
    :-sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
    :-sync id_1 id_2 -> syncs guilds with id 1 and 2
    """
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")






# - - - - -   - - - - -  LOAD COGS  - - - - -  - - - - - #
import time

async def main():
    try:    
      async with bot:  
        for filename in os.listdir('./cogs'):
          if filename != "my_db.py" and filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
        await db.c_table()
        await db.c_embed()
        keep_alive()
        await bot.start(TOKEN)
          
    except discord.errors.HTTPException:
        os.system("echo RATELIMITED, TRYING AGAIN")
        time.sleep(25)
        os.system("kill 1")


asyncio.run(main())

