from dis_snek.models import message_command

from discordbot.command import MtgContext


@message_command('invite')
async def invite(ctx: MtgContext) -> None:
    """Invite me to your server."""
    await ctx.send('Invite me to your discord server by clicking this link: <https://discordapp.com/oauth2/authorize?client_id=224755717767299072&scope=bot&permissions=268757056>')
