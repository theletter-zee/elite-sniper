import discord
from discord.ext import commands


import os
import asyncio

from cogs import my_db as db


PATH = os.path.dirname(os.path.realpath(__file__))


class espanol(commands.Cog):

  async def message_trans(self, lang, section):
    message_dict = {
      'en': {
        'alreadyPrefix': "You're already using the **Default** prefix.",
        'nowDefault': "Now using default prefix `"
      },
      'es': {
        'alreadyPrefix': "Ya estás usando el **valor** prefijo.",
        'nowDefault': "Ahora usando el prefijo predeterminado `"
      }
    }
    return message_dict[lang][section]



  async def getmsg_trans(self, lang, section):
    getmsg_dict = {
      'en': {
        'error': "Nothing to snipe",
        'access_target': "The target has disabled sniping in their `settings`",
        'access_author': "You have disabled sniping in your `settings`"
      },

      'es': {
        'error': "Nada que disparar",
        'access_target': "El objetivo ha deshabilitado el francotirador en su `configuración`",
        'access_author': "Has deshabilitado el francotirador en la `configuración`"
      }
    }
    return getmsg_dict[lang][section]


  async def getedit_trans(self, lang, section):
    getedit_dict = {
      'en': {
        'error': "No recently edited message detected",
        'access_target': "The target has disabled sniping in their `settings`",
        'access_author': "You have disabled sniping in your `settings`"
      },

      'es': {
        'error': "No hay ningún mensaje editado recientemente",
        'access_target': "El objetivo ha deshabilitado el francotirador en su `configuración`",
        'access_author': "Has deshabilitado el francotirador en la `configuración`"
      }
    }
    return getedit_dict[lang][section]




  async def help_trans(self, lang, section):
    help_dict = {
      'en':  {

      # - - Embed Initialized - - #
      'title': "Elite Sniper's commands",
      'desc_a': "<:flag_ea:987500016690163782> **Espanol**\n¿Hablas Español? ",
      'desc_b': " ".join(["If you used the correct command and you still don't see the deleted message/image ",
         "then most likely Discord cleared their cache and the content is gone for good."]),

      # - - Embed Values - - #
      'getmsg_name': "<:white_small_square:987778113599574047> 1. getmsg",
      'getmsg_value': "└ The most recently deleted `message` | alias: `snipe`, `resend`",
      #     -     -     -     -     #
      'getedit_name': "<:white_small_square:987778113599574047> 2. getedit",
      'getedit_value': "└ The most recently deleted `edited` | alias: `snipe`, `resend`",
      #     -     -     -     -     #
      'settings_name': "<:white_small_square:987778113599574047> 3. settings",
      'settings_value': "└ Change your `prefix` | alias: `None`"
    },

    'es':{
      # - - Embed Initialized - - #
      'title': "Elite Sniper's commandos",
      'desc_a': "<:flag_us:996986962844069968> **English**\nSpeak English? ",
      'desc_b': "Si tú usaste el correcto commando y estas no mensaje, entonces Discord eliminado el caché.",

      # - - Embed Values - - #
      'getmsg_name': "<:white_small_square:987778113599574047> 1. recibir",
      'getmsg_value': "└ El más recientemente eliminado `mensaje` | alias: `Ninguno`",
      #     -     -     -     -     #
      'getedit_name': "<:white_small_square:987778113599574047> 2. recibiredit",
      'getedit_value': "└  El más recientemente edito `mensaje` | alias: `Ninguno`",
      #     -     -     -     -     #
      'settings_name': "<:white_small_square:987778113599574047> 3. ajustes",
      'settings_value': "└ Cambiar tu `prefijo` | alias: `Ninguno`"
    }
    }
    return help_dict[lang][section]




  
  async def settings_trans(self, lang, section):
    settings_dict = {
      'en': {
      'changePrefix_A': "Prefix changed! You can type ",
      'changePrefix_B': " to revert to the default prefix.",
      'numError_1': "Prefix must be greater than 0 and less than 4.",
      'numError_2': "I don't have that language or you're already using it.",
      'otherError': "You're not using this command correctly",
      'title': "Settings",
      'desc_a': "Use `",
      'desc_b': "settings (settingNum) (input)`.",
      'changePrefix_name': "<:white_small_square:987778113599574047> 1. Change Prefix",
      'changePrefix_value_a': "└ Change the way you interact with `commands` | eg: `",
      'changePrefix_value_b':  "settings 1 pls`",
      'changeLang_name': "Change Language",
      'changeLang_value_a': "└ Change your current `language` | eg: `",
      'changeLang_value_b': "settings 2 es`",
      'usageName': "<:white_small_square:987778113599574047> 3. Usage",
      'usageValue_a': "└ If disabled, your messages cannot be sniped and you cannot snipe other messages as well. | eg: `",
      'usageDisabled_value_b': "usage on` | Currently: **DISABLED**",
      'usageEnabled_value_a': "usage off` | Currently: **ENABLED**"
      },

      'es': {
        'changePrefix_A': "Prefijo Cambiarse! Tú puedes escribe ",
        'changePrefix_B': " volver.",
        'numError_1': "El prefijo debe ser menor que 4 y mayor que 0",
        'numError_2': "No tengo eso idioma o tú estás usando",
        'otherError': "Tú no usando esta commando correctamente",
        'title': "Ajustes",
        'desc_a': "Usas `",
        'desc_b': "ajustes (ajustesNúm) (tuAporte)`. ",
        'changePrefix_name': "<:white_small_square:987778113599574047> 1. Cambiar Prefijo",
        'changePrefix_value_a': "└ Cambiar tu `comandos` | eg: `",
        'changePrefix_value_b':  "ajustes 1 pls`",
        'changeLang_name': "<:white_small_square:987778113599574047> 2. Cambiar Idioma",
        'changeLang_value_a': "└ Cambiar tu `idioma` | eg: `",
        'changeLang_value_b': "ajustes 2 en`",
        'usageName': "<:white_small_square:987778113599574047> 3. Usar",
        'usageValue_a': "└ Si está deshabilitado, sus mensajes no se dispararán y tampoco podrá disparar otros mensajes. | eg: `",
        'usageDisabled_value_b': "usar on` | Actualmente: **DESHABILITADO**",
        'usageEnabled_value_a': "usar off` | Actualmente: **PERMITIR**"

      }

    }
    return settings_dict[lang][section]

    





  async def usage_trans(self, lang, section):
    usage_dict = {
      'en': {
        'modeError': "You already have this disabled.",

        'modeConfirm': "\n".join(["**Are you sure?** All your messages that has been sniped by other people",
         "will be deleted and you will no longer be able to snipe or get sniped (You can turn this back on",
        "if you change your mind). React to confirm. (Your messages are fine, only the sniped embeds will be deleted)"]),

        'reactError': "You didn't react in time.",

        'usageOff': "You will no longer have your messages sniped & You can no longer snipe messages.  (You can still enable it again)",

        'alreadyEnabled': "You already have this enabled.",
        'alreadyDisabled': 'You already have this disabled',

        'enabled': "You can now snipe deleted messages!",

        'checkSettings': "Check settings for more info on how to use this command."
      },

      'es': {
        'modeError': "Ya ha deshabilitado esto.",

        'modeConfirm': "\n".join(["**¿estás seguro de que?** Todos tus mensajes que han sido sorteados",
         "por otras personas se eliminarán y ya no será capaz de sortear o ser sorteado (puede volver a",
          "activar esto si cambia de opinión). Reaccione para confirmar. (Los mensajes están bien, sólo se eliminarán los incrustaciones de recorte)"]),

        'reactError': "No reaccionaste a tiempo.",

        'usageOff': "Ya no tendrá sus mensajes disparados y ya no podrá disparar mensajes.  (Aún puede habilitarlo nuevamente)",

        'disabled': "Ya ha deshabilitado esto.",
        'enabled': "Ya lo tienes habilitado.",

        'checkSettings': "Compruebe la configuración para obtener más información."
      }
    }
    return usage_dict[lang][section]


    
async def setup(bot):
    await bot.add_cog(espanol(bot))