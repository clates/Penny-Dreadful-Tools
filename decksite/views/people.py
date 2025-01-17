from typing import Sequence

from decksite.data.person import Person
from decksite.view import View


# pylint: disable=no-self-use
class People(View):
    def __init__(self) -> None:
        super().__init__()
        self.show_seasons = True

    def page_title(self) -> str:
        return 'People'
