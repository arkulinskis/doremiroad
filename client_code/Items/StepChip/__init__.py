from anvil import *

from ._anvil_designer import StepChipTemplate


class StepChip(StepChipTemplate):
    """One step of a level on its card: item = {icon, name}."""

    def __init__(self, **properties):
        super().__init__(**properties)
