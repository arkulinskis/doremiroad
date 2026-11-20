from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import PlayTemplate
from ... import dr, game, homework, router

SPEEDS = {"75": 0.75, "50": 0.5}
NEXT_MODE = {"learn": "practice", "practice": "perform"}


def _loose(x):
    """A level dict once loaded (the validator would type it None for good)."""
    return x


class Play(PlayTemplate):
    """#play/<level key>[/75|50], #play/daily and #play/song/<song>/<learn|practice|perform> (Operate, full screen): the
    level engine (Components/Stage) with the pause menu (Dialogs/Pause), the fail card (Dialogs/Fail) and the results
    (Dialogs/Results). Escape or leaving the tab pauses. The result goes to the server (game.act), which checks it and
    hands out the rewards. A road level can run slower (75% / 50%: one star at most, no leaderboard score); failed and
    quit runs still count their playing time in the practice log (game.log_practice)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        a = list(args)
        self._arg = a[0] if a else ""
        self._kind = "daily" if self._arg == "daily" else "song" if self._arg == "song" else "level"
        self._song = a[1] if self._kind == "song" and len(a) > 1 else ""
        self._mode = a[2] if self._kind == "song" and len(a) > 2 and a[2] in game.SONG_MODES else "learn"
        self._speed = SPEEDS.get(a[1], 1.0) if self._kind == "level" and len(a) > 1 else 1.0
        self._x = _loose(None)
        self._level = _loose(None)
        self._pause_open = False
        self._t0 = 0.0
        self._logged = True
        self._keys = anvil.js.report_exceptions(self._on_key)
        self._vis = anvil.js.report_exceptions(self._on_visibility)
        ok = game.ensure()
        if ok and self._kind == "daily":
            self._level = game.S["daily"]["level"]
        elif ok and self._kind == "song":
            self._level = game.song_level(self._song, self._mode)
        elif ok:
            self._x = game.find_level(self._arg)
            if self._x and (game.unlocked(self._arg) or game.rec(self._arg)["stars"]):
                self._level = self._x["l"]
        if self._level is not None and not self._has_rush():
            self._speed = 1.0
        self.missing_box.visible = self._level is None
        self.stage.visible = self._level is not None
        if self._kind == "song":
            self.missing_title.text = "This song isn't on the shelf"
            self.missing_text.text = "It may have been renamed. Pick another one from the Song Shelf."
            self.dom_nodes["missing_link"].setAttribute("href", "#songs")
            self.dom_nodes["missing_link"].textContent = "Open the Song Shelf"

    # ---------------------------------------------------------------- helpers
    def _has_rush(self):
        return any(s.get("t") == "rush" for s in (self._level or {}).get("data", {}).get("steps") or [])

    def _mode_line(self, mode):
        return "%s %s (%s)" % (game.SONG_MODE_ICONS[mode], game.SONG_MODE_NAMES[mode], game.SONG_MODE_SUBS[mode])

    def _subtitle(self):
        if self._kind == "daily":
            return "Daily Practice · " + game.S["today"]
        if self._kind == "song":
            return "Song Shelf · " + self._mode_line(self._mode)
        x = self._x
        line = x["t"]["name"] + (" · Trial" if x["l"]["data"].get("trial") else " · Level %d" % (x["i"] + 1))
        return line + (" · %d%% speed" % round(self._speed * 100) if self._speed < 1 else "")

    def _back(self):
        self.stage.destroy()
        router.go("songs" if self._kind == "song" else "map")

    def _start(self):
        eq = game.S["progress"]["equip"]
        self.stage.start(self._level, self._subtitle(), eq.get("skins") or "classic", eq.get("trails") or "lantern",
                         self._speed)
        self._t0 = dr.now_ms()
        self._logged = False

    def _log_unfinished(self):
        """A run that ended without a saved result (failed, quit, restarted, left): its time goes in the practice log."""
        if self._logged or not self._t0:
            return
        self._logged = True
        game.log_practice((dr.now_ms() - self._t0) / 1000.0, "run")

    def _homework_ticks(self):
        s = homework.stored()
        return (s["hw"], homework.ticks(s["hw"])) if s else (None, [])

    # ---------------------------------------------------------------- page events
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
        if self.stage.running() and not self.stage.is_over():
            self._log_unfinished()
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
            self._log_unfinished()
            self._start()
        elif choice == "quit":
            self._log_unfinished()
            self._back()
        else:
            self.stage.resume()

    def _slower(self):
        """What the fail card offers instead of the same pace again: (button text, what it opens) or None."""
        if self._kind == "song":
            if self._mode == "perform":
                return "🎯 Practice it at 70% speed", "practice"
            if self._mode == "practice":
                return "🐢 Learn it note by note", "learn"
            return None
        if self._kind == "level" and self._has_rush() and self._speed > 0.5:
            nxt = 0.75 if self._speed >= 1 else 0.5
            return "🐢 Try at %d%% speed" % round(nxt * 100), nxt
        return None

    @handle("stage", "failed")
    def stage_failed(self, info, **event_args):
        from ...Dialogs.Fail import Fail
        self._log_unfinished()
        dr.sfx("fail")
        slower = self._slower()
        meter = info.get("reason") == "meter"
        if meter:
            text = "Too many misses in a row emptied the harmony meter. Watch the falling notes and land them on the line."
            if slower and self._kind == "level":
                text += " A slower run still clears the level."
        else:
            text = ("You reached %d%% accuracy; this one needs %d%%. Every attempt makes the road shorter."
                    % (round(info.get("accuracy") or 0), round(info.get("pass") or 0)))
        choice = alert(Fail(kicker=self._level["name"], title="The harmony broke" if meter else "Not quite there", text=text,
                            slower_text=slower[0] if slower else "",
                            back_text="Back to the Song Shelf" if self._kind == "song" else "Back to the map"),
                       buttons=[], role="app-dialog", dismissible=False)
        if choice == "slower" and slower:
            if self._kind == "song":
                router.go("play", "song", self._song, slower[1])
                return
            self._speed = float(slower[1])
            router.replace("play", self._arg, str(int(round(self._speed * 100))))
            self._start()
            return
        self._after(choice)

    @handle("stage", "finished")
    def stage_finished(self, result, accuracy, **event_args):
        from ...Dialogs.Fail import Fail
        from ...Dialogs.Results import Results
        self._logged = True  # the server logs a finished run's time itself
        hw, before = self._homework_ticks()
        if self._kind == "daily":
            r = game.act("finish_daily", result)
        elif self._kind == "song":
            r = game.act("finish_song", self._song, self._mode, result)
        else:
            if self._speed < 1:
                result["speed"] = self._speed
            r = game.act("finish_level", self._arg, result)
        router.refresh_shell()
        if not r:
            choice = alert(Fail(kicker=self._level["name"], title="That didn't save",
                                text="Your run couldn't be recorded. Check your connection and try again.",
                                back_text="Back to the Song Shelf" if self._kind == "song" else "Back to the map"),
                           buttons=[], role="app-dialog", dismissible=False)
            self._after(choice)
            return
        report = dict(r["report"])
        if hw is not None:  # homework items this run ticked off
            after = homework.ticks(hw)
            ticked = []
            for i, t in enumerate(hw["x"]):
                if after[i] and not before[i]:
                    ticked.append(homework.task_label(t)[0])
            report["hw_ticked"] = ticked
            sm = homework.summary(hw)
            report["hw_count"] = "%d of %d done" % (sm["done"], sm["total"])
        if self._kind == "song":
            nxt = NEXT_MODE.get(self._mode)
            res = Results(report=report, key=None, name=self._level["name"], where="Song Shelf · " + self._mode_line(self._mode),
                          next_text=("Next: %s %s ▸" % (game.SONG_MODE_ICONS[nxt], game.SONG_MODE_NAMES[nxt])) if nxt else "",
                          back_text="Back to the Song Shelf")
        else:
            res = Results(report=report, key=None if self._kind == "daily" else self._arg, name=self._level["name"])
        choice = alert(res, buttons=[], large=True, role="app-dialog", dismissible=False)
        if choice == "next" and self._kind == "song" and NEXT_MODE.get(self._mode):
            router.go("play", "song", self._song, NEXT_MODE[self._mode])
        elif choice == "next" and res.next_key:
            game.S["sel"] = res.next_terr
            router.go("play", res.next_key)
        elif choice == "again":
            self._start()
        else:
            if res.map_terr and self._kind != "song":
                game.S["sel"] = res.map_terr
            self._back()

    def _after(self, choice):
        if choice == "retry":
            self._start()
        else:
            self._back()
