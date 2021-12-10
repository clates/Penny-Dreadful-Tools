import subprocess
import sys

import dis_snek.const
from dis_snek.models.application_commands import slash_command

from discordbot.command import MtgContext
from magic import database


@slash_command('version')
async def version(ctx: MtgContext) -> None:
    """Display the current version numbers"""
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], universal_newlines=True).strip('\n').strip('"')
    age = subprocess.check_output(['git', 'show', '-s', '--format=%ci ', 'HEAD'], universal_newlines=True).strip('\n').strip('"')
    scryfall = database.last_updated()
    await ctx.send(f'I am currently running mtgbot version `{commit}` ({age}), and scryfall last updated `{scryfall}`\nPython `{sys.version}`, dis_snek {dis_snek.const.__version__}')
