import re

from dis_snek.client import Snake
from dis_snek.models import Scale, slash_command

from discordbot import command
from discordbot.command import MtgContext
from magic import image_fetcher
from magic.models import Card


class Art(Scale):
    @slash_command('art')
    @command.slash_card_option()
    async def art(self, ctx: MtgContext, card: Card) -> None:
        """Display the artwork of the requested card."""

        if card is not None:
            file_path = re.sub('.jpg$', '.art_crop.jpg', image_fetcher.determine_filepath([card]))
            success = await image_fetcher.download_scryfall_card_image(card, file_path, version='art_crop')
            if success:
                await ctx.send_image_with_retry(file_path)
            else:
                await ctx.send('{author}: Could not get image.'.format(author=ctx.author.mention))

    art.autocomplete('card')(command.autocomplete_card)

    m_art = command.alias_message_command_to_slash_command(art)

def setup(bot: Snake) -> None:
    Art(bot)
