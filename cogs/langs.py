#A text map would be a better approach instead of having to do something like this.

import discord
from discord.ext import commands


import os
import asyncio
import json

from cogs import my_db as db
import cache as ch



PATH = os.path.dirname(os.path.realpath(__file__))

class Promobuttons(discord.ui.View):
  
  def __init__(self):
      super().__init__()
    
      url_top = "https://top.gg/bot/800136653041303553/vote"
      url_bot = "https://github.com/theletter-zee/snipe-bot"
  
      self.add_item(discord.ui.Button(label='Votar en Top.gg!', url=url_top))
      self.add_item(discord.ui.Button(label='crea tu propio bot de snipe!', url=url_bot))


class espanol(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  async def sp_help(self, ctx):

    async with db.get_db(f"{PATH}/data/users.db") as c:    
      c.execute("SELECT prefix FROM user WHERE user_id = ?", (ctx.author.id,))
      prefix = c.fetchone()[0]

    help_Embed = discord.Embed(title='Elite Sniper\'s commandos',
    description=f"<:flag_us:996986962844069968> **English**\nSpeak English? `{prefix}settings 2 en` "+
                f"\n---------------\n"+
                f"Si tú usaste el correcto commando y estas no mensaje, entonces Discord eliminado el caché.",
    color=0x459fa5)

    help_Embed.add_field(name='<:white_small_square:987778113599574047> 1.  recibir',value=f'└ El más recientemente eliminado `mensaje` | alias: `Ninguno`',inline=True)
    help_Embed.add_field(name='<:white_small_square:987778113599574047> 2. recibiredit',value=f'└  El más recientemente edito `mensaje` | alias: `Ninguno`',inline=True)
    help_Embed.add_field(name='<:white_small_square:987778113599574047> 3. ajustes',value=f'└ Cambiar tu `prefijo` | alias: `Ninguno`',inline=True)
    #help_Embed.set_footer(text=f"Uso {prefix}reporte (mensaje) a reporte un problemo con le bot.")

    await ctx.channel.send(embed=help_Embed, view=Promobuttons())
    await db.update_help(ctx.author.id)




  
  async def sp_settings(self, ctx, num=0, change=None):
    async with db.get_db(f"{PATH}/data/users.db") as c:  
      c.execute("SELECT prefix FROM user WHERE user_id = ?;", (ctx.author.id,))
      prefix = c.fetchone()[0]
      c.execute("SELECT access FROM user WHERE user_id = ?;", (ctx.author.id,))
      access_author = c.fetchone()[0]

    if num > 0 and num <=3:
    
      #Cambiar prefijo 
      if num == 1 and change is not None and len(change) <=3 and len(change) > 0:
        ch.prefix_cache.update({ctx.author.id : change})
        await db.update_prefix(ctx.author.id, change)
        return await ctx.channel.send(f"Prefijo Cambiarse! Tú puedes escribe \"{self.bot.user.mention} **..**\" volver.")
      
      #Cambiar Idioma
      elif num == 2 and change == 'en':
        await db.update_lang(ctx.author.id, change)
        return await ctx.channel.send("✅")

      else:
        if num == 1:
          return await ctx.channel.send("El prefijo debe ser menor que 4 y mayor que 0")
        elif num == 2:
          return await ctx.channel.send("No tengo eso idioma o tú estás usando")
        else:
          return await ctx.channel.send("Tú no usando esta commando correctamente")

    settings_em = discord.Embed(title="Ajustes", description=f"Usas `{prefix}ajustes (ajustesNúm) (tuAporte)`. ", color=0x459fa5)
    settings_em.add_field(name="<:white_small_square:987778113599574047> 1. Cambiar Prefijo", value=f"└ Cambiar tu `comandos` | eg: `{prefix}ajustes 1 pls`")
    settings_em.add_field(name="<:white_small_square:987778113599574047> 2. Cambiar Idioma", value=f"└ Cambiar tu `idioma` | eg: `{prefix}ajustes 2 en`")
    
    if access_author == 0:
      #Snipe es deshabilitado - show X
      settings_em.add_field(name="<:white_small_square:987778113599574047> 3. Usar", value=f"└ Si está deshabilitado, sus mensajes no se dispararán y tampoco podrá disparar otros mensajes. | eg: `{prefix}uso on` | Actualmente: **DESHABILITADO**")
      settings_em.set_footer(text="El prefijo debe ser menor que 4 y mayor que 0")
      return await ctx.send(embed=settings_em)
    else:

      settings_em.add_field(name="<:white_small_square:987778113599574047> 3. Usar", value=f"└ Si está deshabilitado, sus mensajes no se dispararán y tampoco podrá disparar otros mensajes. | eg: `{prefix}uso off` | Actualmente: **PERMITIR**")
      settings_em.set_footer(text="El prefijo debe ser menor que 4 y mayor que 0")
    
      await ctx.send(embed=settings_em)







  async def sp_usage(self, ctx, mode):
    async with db.get_db(f"{PATH}/data/users.db") as c:  
      c.execute("SELECT access FROM user WHERE user_id = ?;", (ctx.author.id,))
      access_author = c.fetchone()[0]

    def check(reaction, user):
      return user == ctx.author and str(reaction.emoji) == '👍'

    if mode == "off":
      if access_author == 0:
        return await ctx.channel.send("Ya ha deshabilitado esto.")

      msg = await ctx.channel.send("**¿estás seguro de que?** Todos tus mensajes que han sido sorteados por otras personas se eliminarán y ya no será capaz de sortear o ser sorteado (puede volver a activar esto si cambia de opinión). Reaccione para confirmar. (Los mensajes están bien, sólo se eliminarán los incrustaciones de recorte)")
      await msg.add_reaction('👍')

      try:
        reaction, user = await self.bot.wait_for('reaction_add', timeout=35, check=check)
      except asyncio.TimeoutError:
        await ctx.channel.send("No reaccionaste a tiempo.")
      else:
        embeds = await db.read_db()
        try:
          for chan in embeds[str(ctx.author.id)]:
            channel = self.bot.get_channel(int(chan))
            
            for msg_id in embeds[str(ctx.author.id)][str(chan)]['msg_id']:
              msg = await channel.fetch_message(msg_id)
              await msg.delete()
        except:
          print("\n\n Original Embed was deleted, skipping ")

        embeds.pop(str(ctx.author.id))
        with open(PATH+"/data/embed.json", 'w') as f:
          json.dump(embeds, f, indent=2)
          

        await db.update_access(ctx.author.id, 0)
        return await ctx.channel.send("Ya no tendrá sus mensajes disparados y ya no podrá disparar mensajes.  (Aún puede habilitarlo nuevamente)")
    elif mode == 'on':
      if access_author == 1:
        return await ctx.channel.send("Ya lo tienes habilitado.")

      await db.update_access(ctx.author.id, 1)
      return await ctx.channel.send("¡ahora puedes disparar mensajes eliminados!")
    else:
      await ctx.channel.send("Compruebe la configuración para obtener más información.")

    
async def setup(bot):
    await bot.add_cog(espanol(bot))