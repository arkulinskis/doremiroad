from anvil import *

from ._anvil_designer import DailyCardTemplate
from ... import dr, game, state


class DailyCard(DailyCardTemplate):
    """Today's Daily Practice (a level the server generates for the date). Closes with "play" on Start."""

    def __init__(self, **properties):
        super().__init__(**properties)
        S = game.S
        d, l = S["daily"], S["daily"]["level"]
        state.heading(self.title_label, 2)
        self.where_label.text = "Every day · " + S["today"]
        self.intro_label.text = l["data"].get("intro") or ""
        self.steps_panel.items = [{"icon": dr.step_icon(s.get("t")), "name": s.get("prompt") or dr.step_name(s.get("t"))}
                                  for s in l["data"]["steps"]]
        rw = S["catalog"]["rewards"]
        if d["done"]:
            self.rewards_panel.items = [{"icon": "✓", "text": "Already done today: practise for fun, rewards return tomorrow."}]
        else:
            ducats = rw["daily_ducats"] + rw["daily_streak_bonus"] * min(d["streak"], rw["daily_streak_cap"] - 1)
            self.rewards_panel.items = [{"icon": "🪙", "text": "%d ducats (more with a streak)" % ducats},
                                        {"icon": "✨", "text": "%d XP" % rw["xp_daily"]},
                                        {"icon": "🃏", "text": "A chance of a composer card"}]

    @handle("start_button", "click")
    def start_button_click(self, **event_args):
        dr.sfx("click")
        self.raise_event("x-close-alert", value="play")
