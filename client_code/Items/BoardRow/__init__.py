from anvil import *

from ._anvil_designer import BoardRowTemplate


class BoardRow(BoardRowTemplate):
    """A leaderboard line: item = {rank, name, score, you}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.rank_label.text = str(self.item["rank"])
        self.name_label.text = self.item["name"]
        self.score_label.text = self.item["score"]
        self.row.classes["you"] = bool(self.item.get("you"))
