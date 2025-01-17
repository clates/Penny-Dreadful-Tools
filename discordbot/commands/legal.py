from dis_snek import Snake
from dis_snek.models import Scale, slash_command

from discordbot import command
from discordbot.command import MtgContext
from magic.models import Card


class Legal(Scale):
    @slash_command('legal')
    @command.slash_card_option()
    async def legal(self, ctx: MtgContext, card: Card) -> None:
        """Announce whether the specified card is legal or not."""
        await ctx.single_card_text(card, lambda c: '')

    legal.autocomplete('card')(command.autocomplete_card)

    m_legal = command.alias_message_command_to_slash_command(legal)

def setup(bot: Snake) -> None:
    Legal(bot)
