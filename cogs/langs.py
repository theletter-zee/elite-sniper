#For the future I'll test out using a global dictionary in main.py

import discord
from discord.ext import commands


import os

from cogs import my_db as db
import cache as ch



PATH = os.path.dirname(os.path.realpath(__file__))

class Promobuttons(discord.ui.View):
  
  def __init__(self):
      super().__init__()
    
      url_top = "https://top.gg/bot/800136653041303553/vote"
      url_bot = "https://example.com/"
  
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

      #Apagar disparando
      elif num == 3 and change == 'off':
        await db.update_access(ctx.author.id, 0)
        return await ctx.channel.send("Ya no tendrá sus mensajes disparados y ya no podrá disparar mensajes.")
      
      else:
        if num == 1:
          return await ctx.channel.send("El prefijo debe ser menor que 4 y mayor que 0")
        elif num == 2:
          return await ctx.channel.send("No tengo eso idioma o tú estás usando")
        elif num == 3 and change == 'on' and access_author == 0:
          await db.update_access(ctx.author.id, 1)
          return await ctx.channel.send("¡Ahora puedes disparar mensajes eliminados!")
        else:
          return await ctx.channel.send("Tú no usando esta commando correctamente")

    settings_em = discord.Embed(title="Ajustes", description=f"Usas `{prefix}ajustes (ajustesNúm) (tuAporte)`. ", color=0x459fa5)
    settings_em.add_field(name="<:white_small_square:987778113599574047> 1. Cambiar Prefijo", value=f"└ Cambiar tu `comandos` | eg: `{prefix}ajustes 1 pls`")
    settings_em.add_field(name="<:white_small_square:987778113599574047> 2. Cambiar Idioma", value=f"└ Cambiar tu `idioma` | eg: `{prefix}ajustes 2 en`")
    if access_author == 0:
      #Snipe es deshabilitado - show X
      settings_em.add_field(name="<:white_small_square:987778113599574047> 3. Usar", value=f"└ Si está deshabilitado, sus mensajes no se dispararán y tampoco podrá disparar otros mensajes. | eg: `{prefix}ajustes 3 on` | Actualmente: **DESHABILITADO**")
    
    settings_em.add_field(name="<:white_small_square:987778113599574047> 3. Usar", value=f"└ Si está deshabilitado, sus mensajes no se dispararán y tampoco podrá disparar otros mensajes. | eg: `{prefix}ajustes 3 off` | Actualmente: **PERMITIR**")
    settings_em.set_footer(text="El prefijo debe ser menor que 4 y mayor que 0")
    
    await ctx.send(embed=settings_em)

    
async def setup(bot):
    await bot.add_cog(espanol(bot))