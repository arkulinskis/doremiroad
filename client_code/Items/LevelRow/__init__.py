from anvil import *

from ._anvil_designer import LevelRowTemplate
from ... import state


class LevelRow(LevelRowTemplate):
    """A level in the territory card. item = {key, name, i, stars, best, open, trial, banner, icons}.
    Clicking an open or cleared level raises x-level on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        cleared, opened = it["stars"] > 0, it["open"]
        self.row.classes.update({"done": cleared, "open": opened and not cleared, "locked": not opened and not cleared,
                                 "trial": it["trial"]})
        if cleared:
            self.node.style["background"] = it["banner"]
        self.node_text.text = ("⚑" if it["trial"] else str(it["i"] + 1)) if (opened or cleared) else "🔒"
        self.name_label.text = it["name"]
        status = ("Best %d%%" % round(it["best"])) if cleared else ("Ready" if opened else "Locked")
        self.sub_label.text = status + (" · " + it["icons"] if it["icons"] else "")
        self.stars_label.text = ("★" * it["stars"] + "☆" * (3 - it["stars"])) if (opened or cleared) else ""
        state.set_attr(self.row, "aria-label", "%s: %s%s" % (it["name"], status,
                                                            ", %d of 3 stars" % it["stars"] if cleared else ""))
        if not (opened or cleared):
            state.set_attr(self.row, "aria-disabled", "true")

    def row_click(self, event):
        event.preventDefault()
        if self.item["open"] or self.item["stars"]:
            self.parent.raise_event("x-level", key=self.item["key"])
