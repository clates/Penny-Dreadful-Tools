
from dis_snek import Snake
from dis_snek.models import Scale, message_command

from discordbot.command import MtgMessageContext


class Barbs(Scale):
    @message_command()
    async def barbs(self, ctx: MtgMessageContext) -> None:
        """Volvary's advice for when to board in Aura Barbs."""
        msg = "Heroic doesn't get that affected by Barbs. Bogles though. Kills their creature, kills their face."
        await ctx.send(msg)

def setup(bot: Snake) -> None:
    Barbs(bot)
