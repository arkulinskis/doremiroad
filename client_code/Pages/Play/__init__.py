from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import PlayTemplate
from ... import dr, game, router


def _loose(x):
    """A level dict once loaded (the validator would type it None for good)."""
    return x


class Play(PlayTemplate):
    """#play/<level key> and #play/daily (Operate, full screen): the level engine (Components/Stage) with the pause
    menu (Dialogs/Pause), the fail card (Dialogs/Fail) and the results (Dialogs/Results). Escape or leaving the tab
    pauses. The result goes to the server (game.act), which checks it and hands out the rewards."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self._arg = args[0] if args else ""
        self._daily = self._arg == "daily"
        self._x = _loose(None)
        self._level = _loose(None)
        self._pause_open = False
        self._keys = anvil.js.report_exceptions(self._on_key)
        self._vis = anvil.js.report_exceptions(self._on_visibility)
        ok = game.ensure()
        if ok and self._daily:
            self._level = game.S["daily"]["level"]
        elif ok:
            self._x = game.find_level(self._arg)
            if self._x and (game.unlocked(self._arg) or game.rec(self._arg)["stars"]):
                self._level = self._x["l"]
        self.missing_box.visible = self._level is None
        self.stage.visible = self._level is not None

    def _subtitle(self):
        if self._daily:
            return "Daily Practice · " + game.S["today"]
        x = self._x
        return x["t"]["name"] + (" · Trial" if x["l"]["data"].get("trial") else " · Level %d" % (x["i"] + 1))

    def _start(self):
        eq = game.S["progress"]["equip"]
        self.stage.start(self._level, self._subtitle(), eq.get("skins") or "classic", eq.get("trails") or "lantern")

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(False)
        window.document.addEventListener("keydown", self._keys)
        window.document.addEventListener("visibilitychange", self._vis)
        if self._level is not None:
            self._start()

    def leave(self):
        window.document.removeEventListener("keydown", self._keys)
        window.document.removeEventListener("visibilitychange", self._vis)
        self.stage.destroy()

    def _on_key(self, event):
        if getattr(event, "key", None) == "Escape" and not self._pause_open and self.stage.running() and not self.stage.is_over():
            self.stage_paused()

    def _on_visibility(self, event):
        if window.document.hidden and self.stage.running() and not self.stage.is_paused() and not self.stage.is_over():
            self.stage_paused()

    @handle("stage", "paused")
    def stage_paused(self, **event_args):
        if self._pause_open or not self.stage.running():
            return
        from ...Dialogs.Pause import Pause
        from ...Dialogs.Settings import Settings
        self._pause_open = True
        self.stage.pause()
        try:
            choice = alert(Pause(), buttons=[], role="app-dialog", dismissible=True)
            while choice == "settings":
                alert(Settings(), buttons=[], large=True, role="app-dialog", dismissible=True)
                self.stage.relabel()
                choice = alert(Pause(), buttons=[], role="app-dialog", dismissible=True)
        finally:
            self._pause_open = False
        dr.sfx("click")
        if choice == "restart":
            self._start()
        elif choice == "quit":
            self.stage.destroy()
            router.go("map")
        else:
            self.stage.resume()

    @handle("stage", "failed")
    def stage_failed(self, info, **event_args):
        from ...Dialogs.Fail import Fail
        dr.sfx("fail")
        meter = info.get("reason") == "meter"
        if meter:
            text = ("Too many misses in a row emptied the harmony meter. Slow down, watch the falling notes, "
                    "and land them on the line.")
        else:
            text = ("You reached %d%% accuracy; this level needs %d%%. Every attempt makes the road shorter."
                    % (round(info.get("accuracy") or 0), round(info.get("pass") or 0)))
        choice = alert(Fail(kicker=self._level["name"], title="The harmony broke" if meter else "Not quite there", text=text),
                       buttons=[], role="app-dialog", dismissible=False)
        self._after(choice)

    @handle("stage", "finished")
    def stage_finished(self, result, accuracy, **event_args):
        from ...Dialogs.Fail import Fail
        from ...Dialogs.Results import Results
        if self._daily:
            r = game.act("finish_daily", result)
        else:
            r = game.act("finish_level", self._arg, result)
        router.refresh_shell()
        if not r:
            choice = alert(Fail(kicker=self._level["name"], title="That didn't save",
                                text="Your run couldn't be recorded. Check your connection and try again."),
                           buttons=[], role="app-dialog", dismissible=False)
            self._after(choice)
            return
        res = Results(report=r["report"], key=None if self._daily else self._arg, name=self._level["name"])
        choice = alert(res, buttons=[], large=True, role="app-dialog", dismissible=False)
        if choice == "next" and res.next_key:
            game.S["sel"] = res.next_terr
            router.go("play", res.next_key)
        elif choice == "again":
            self._start()
        else:
            if res.map_terr:
                game.S["sel"] = res.map_terr
            router.go("map")

    def _after(self, choice):
        if choice == "retry":
            self._start()
        else:
            self.stage.destroy()
            router.go("map")
