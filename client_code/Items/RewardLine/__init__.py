from anvil import *

from ._anvil_designer import RewardLineTemplate


class RewardLine(RewardLineTemplate):
    """A reward on a level or daily card: item = {icon, text}."""

    def __init__(self, **properties):
        super().__init__(**properties)
