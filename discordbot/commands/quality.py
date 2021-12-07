from dis_snek.annotations.argument_annotations import CMD_BODY
from dis_snek.models.command import message_command

from discordbot.command import MtgContext


@message_command('quality')
async def quality(ctx: MtgContext, product: CMD_BODY = None) -> None:
    """A reminder about everyone's favorite way to play digital Magic"""
    if product is None:
        product = 'Magic Online'
    await ctx.send(f'**{product}** is a Quality™ Program.')
