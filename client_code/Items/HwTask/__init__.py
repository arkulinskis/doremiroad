from anvil import *

from ._anvil_designer import HwTaskTemplate
from ... import state


class HwTask(HwTaskTemplate):
    """One homework line. item = {i, task, title, sub, done, view}: view "kid" (a tick and Play), "teacher" (Remove)
    or "report" (a tick only). Play raises x-play (task) and Remove x-remove (i) on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        view = it.get("view") or "kid"
        done = bool(it.get("done"))
        ticks = view != "teacher"
        self.row.classes.update({"done": ticks and done, "teacher": view == "teacher", "goal": bool(it.get("goal"))})
        self.dom_nodes["tick"].textContent = ("✓" if done else "") if ticks else str(it.get("i", 0) + 1)
        self.title_label.text = it["title"]
        self.sub_label.text = it.get("sub") or ""
        self.sub_label.visible = bool(it.get("sub"))
        self.play_button.visible = view == "kid" and bool(it.get("task"))
        self.play_button.text = "Again ▸" if done else "Play ▸"
        self.play_button.role = ["btn", "btn-sm"] if done else ["btn", "btn-sm", "btn-primary"]
        self.remove_button.visible = view == "teacher"
        state.set_control_attr(self.play_button, "aria-label", "Play %s" % it["title"])
        state.set_control_attr(self.remove_button, "aria-label", "Remove %s" % it["title"])
        if ticks:
            state.set_attr(self.row, "aria-label", "%s: %s" % (it["title"], "done" if done else "not done yet"))

    @handle("play_button", "click")
    def play_button_click(self, **event_args):
        self.parent.raise_event("x-play", task=self.item["task"])

    @handle("remove_button", "click")
    def remove_button_click(self, **event_args):
        self.parent.raise_event("x-remove", i=self.item["i"])
