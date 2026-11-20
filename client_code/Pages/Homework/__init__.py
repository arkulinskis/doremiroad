from anvil import *

from ._anvil_designer import HomeworkTemplate
from ... import dr, game, homework, router, state


def _loose(x):
    return x


class Homework(HomeworkTemplate):
    """#hw/<code> (a teacher's link: kept in this browser) and #hw (the kept one), plus #hw/<code>/preview for the
    teacher (not kept). The checklist ticks itself from the practice log (homework.py); Play opens each task."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.tasks_panel.add_event_handler("x-play", self._play)
        state.heading(self.title_label, 1)
        self._preview = len(args) > 1 and args[1] == "preview"
        code = args[0] if args else ""
        self._hw = _loose(None)
        broken = False
        if code:
            hw = homework.parse(code)
            if hw is None:
                broken = True
            else:
                self._hw = hw
                if not self._preview:
                    old = homework.stored()
                    homework.save(code, hw)
                    if old and old["code"] != code:
                        state.toast("New homework from %s. It replaces the one you had." % homework.teacher_name(hw))
        else:
            s = homework.stored()
            self._hw = s["hw"] if s else None
        self.broken_box.visible = broken
        self.empty_box.visible = not broken and self._hw is None
        self.main_box.visible = self._hw is not None
        if self._hw is not None:
            game.ensure()
            self._draw()

    def _draw(self):
        hw = self._hw
        today = dr.today()
        self.preview_label.visible = self._preview
        self.title_label.text = "Homework from %s" % (hw["t"] or "your teacher")
        self.due_label.text = homework.due_text(hw["d"], today).capitalize() + " · sent %s" % homework.nice_date(hw["f"])
        self.note_label.text = "“%s”" % hw["n"] if hw["n"] else ""
        self.note_label.visible = bool(hw["n"])
        if not game.ready():
            rows = [{"i": i, "task": "", "title": t, "sub": "", "done": False, "view": "report"}
                    for i, t in enumerate(hw["x"])]
            self.tasks_panel.items = rows
            self.progress_label.text = "Couldn't load your progress. Check your connection."
            self.done_label.visible = False
            return
        sm = homework.summary(hw)
        rows = []
        for i, t in enumerate(hw["x"]):
            title, sub = homework.task_label(t)
            rows.append({"i": i, "task": t, "title": title, "sub": sub, "done": sm["ticks"][i], "view": "kid"})
        if sm["need"]:
            rows.append({"i": len(rows), "task": "", "title": homework.goal_text(hw),
                         "sub": "%d of %d days so far. Every minute you play counts, even when a run fails." % (sm["met"], sm["need"]),
                         "done": sm["met"] >= sm["need"], "view": "kid", "goal": True})
        self.tasks_panel.items = rows
        self.progress_label.text = "%d of %d done" % (sm["done"], sm["total"])
        self.dom_nodes["bar"].style.width = "%d%%" % (int(100 * sm["done"] / sm["total"]) if sm["total"] else 0)
        self.done_label.visible = sm["all"]

    def _play(self, task, **event_args):
        dr.sfx("click")
        args, why = homework.task_target(task)
        if why:
            state.toast(why)
            return
        router.go("play", *args)

    @handle("remove_button", "click")
    def remove_button_click(self, **event_args):
        if confirm("Remove this homework from this browser? You can open the teacher's link again to get it back."):
            if not self._preview:
                homework.clear()
            router.go("hw")
            router.refresh_shell()

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(True)
