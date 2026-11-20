from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import TeacherTemplate
from ... import dr, game, homework, router, state


def _base_url():
    return str(window.location.href).split("#")[0]


class Teacher(TeacherTemplate):
    """#teacher (Operate): a piano teacher builds a homework link. Up to six tasks (a song and how to play it, a road
    level, Daily Practice), a weekly goal, a due date and a note. The link carries everything (homework.py); nothing is
    saved on the server. The teacher's last choices are kept in this browser (localStorage dr.teacher)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        self.tasks_panel.add_event_handler("x-remove", self._remove)
        self._kind = "song"
        self._mode = "practice"
        self._tasks: list = []
        self._code = ""
        state.set_control_attr(self.item_drop, "aria-label", "Which one")
        state.set_control_attr(self.mins_drop, "aria-label", "Minutes a day")
        state.set_control_attr(self.days_drop, "aria-label", "Days a week")
        state.set_control_attr(self.name_box, "maxlength", "30")
        state.set_control_attr(self.name_box, "autocomplete", "name")
        state.set_control_attr(self.note_box, "maxlength", "200")
        state.set_control_attr(self.link_box, "readonly", "readonly")
        state.set_control_attr(self.link_box, "aria-label", "The homework link")
        state.live(self.copied_label)
        self.result_box.visible = False
        self.error_label.visible = False
        ok = game.ensure()
        self.main_box.visible = ok
        self.failed_box.visible = not ok
        if not ok:
            return
        self.mins_drop.items = [("No minutes goal", 0)] + [("%d minutes" % m, m) for m in homework.MINUTES if m]
        self.days_drop.items = [("%d day%s a week" % (d, "" if d == 1 else "s"), d) for d in range(1, 8)]
        today = dr.today()
        self.due_drop.items = [("%s (%s)" % (homework.nice_date(homework.add_days(today, n)),
                                             "tomorrow" if n == 1 else "in a week" if n == 7 else "in %d days" % n), n)
                               for n in (1, 2, 3, 4, 5, 6, 7, 10, 14)]
        draft = dr.store_get(homework.TEACHER_STORE, None) or {}
        self.name_box.text = str(draft.get("t") or "")[:30]
        self.note_box.text = str(draft.get("n") or "")[:200]
        self.mins_drop.selected_value = draft.get("m") if draft.get("m") in homework.MINUTES else 15
        self.days_drop.selected_value = draft.get("k") if draft.get("k") in range(1, 8) else 5
        self.due_drop.selected_value = draft.get("due") if draft.get("due") in (1, 2, 3, 4, 5, 6, 7, 10, 14) else 7
        self._tasks = [t for t in (draft.get("x") or []) if isinstance(t, str) and homework.TASK_RE.match(t)][:homework.MAX_TASKS]
        self._draw_kind()
        self._draw_tasks()

    # ---------------------------------------------------------------- picking tasks
    def _draw_kind(self):
        for v, el in (("song", self.k_song), ("level", self.k_level), ("daily", self.k_daily)):
            el.classes["on"] = self._kind == v
        for v, el in (("learn", self.m_learn), ("practice", self.m_practice), ("perform", self.m_perform)):
            el.classes["on"] = self._mode == v
        self.item_field.visible = self._kind != "daily"
        self.mode_field.visible = self._kind == "song"
        self.daily_note.visible = self._kind == "daily"
        if self._kind == "song":
            self.dom_nodes["item_caption"].textContent = "Song"
            self.item_drop.items = [(s["title"] + (" 🎄" if s["shelf"] == "christmas" else ""), s["key"])
                                    for s in game.S["songs"]["songs"]]
        elif self._kind == "level":
            self.dom_nodes["item_caption"].textContent = "Level on the road"
            self.item_drop.items = [("%s · %s %s" % (x["t"]["name"], "Trial:" if x["l"]["data"].get("trial")
                                                     else "%d." % (x["i"] + 1), x["l"]["name"]), x["l"]["key"])
                                    for x in game.all_levels()]
        state.set_control_attr(self.item_drop, "aria-label", "Which song" if self._kind == "song" else "Which level")

    def kind_click(self, event):
        self._kind = str(event.currentTarget.getAttribute("data-v"))
        self._draw_kind()

    def mode_click(self, event):
        self._mode = str(event.currentTarget.getAttribute("data-v"))
        self._draw_kind()

    def _draw_tasks(self):
        rows = []
        for i, t in enumerate(self._tasks):
            title, sub = homework.task_label(t)
            rows.append({"i": i, "task": t, "title": title, "sub": sub, "done": False, "view": "teacher"})
        self.tasks_panel.items = rows
        self.tasks_empty.visible = not rows
        full = len(self._tasks) >= homework.MAX_TASKS
        self.add_button.enabled = not full
        self.add_button.text = "That's six: the most one link holds" if full else "＋ Add to the homework"

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        if self._kind == "daily":
            t = "d"
        elif self._kind == "song":
            t = "s:%s:%s" % (self.item_drop.selected_value, self._mode)
        else:
            t = "l:%s" % self.item_drop.selected_value
        if t in self._tasks:
            state.toast("That's already on the list.")
            return
        if len(self._tasks) >= homework.MAX_TASKS:
            return
        dr.sfx("click")
        self._tasks.append(t)
        self._changed()
        self._draw_tasks()

    def _remove(self, i, **event_args):
        if 0 <= i < len(self._tasks):
            self._tasks.pop(i)
        self._changed()
        self._draw_tasks()

    def _changed(self):
        self.result_box.visible = False
        self.error_label.visible = False

    # ---------------------------------------------------------------- the link
    @handle("make_button", "click")
    def make_button_click(self, **event_args):
        if not self._tasks:
            self.error_label.text = "Add at least one song, level or the Daily Practice first (part 1)."
            self.error_label.visible = True
            return
        self.error_label.visible = False
        name = (self.name_box.text or "").strip()
        note = (self.note_box.text or "").strip()
        mins = self.mins_drop.selected_value or 0
        days = self.days_drop.selected_value or 0
        due_in = self.due_drop.selected_value or 7
        today = dr.today()
        hw = homework.make(name, note, homework.add_days(today, due_in), mins, days, self._tasks, today)
        self._code = homework.encode(hw)
        dr.store_set(homework.TEACHER_STORE, {"t": name, "n": note, "m": mins, "k": days, "due": due_in, "x": self._tasks})
        self.link_box.text = _base_url() + "#hw/" + self._code
        self.dom_nodes["preview_link"].setAttribute("href", router.href("hw", self._code, "preview"))
        self.copied_label.text = ""
        self.result_box.visible = True
        self.share_button.visible = bool(getattr(window.navigator, "share", None))
        dr.sfx("unlock")
        state.focus(self.copy_button)

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        try:
            window.navigator.clipboard.writeText(self.link_box.text)
            self.copied_label.text = "Copied. Paste it into a text, an email or your studio app."
        except Exception:
            getattr(state.control(self.link_box), "select")()
            self.copied_label.text = "Select the link above and copy it (Ctrl+C, or long-press on a phone)."

    @handle("share_button", "click")
    def share_button_click(self, **event_args):
        who = (self.name_box.text or "").strip()
        try:
            window.navigator.share({"title": "Piano homework", "url": self.link_box.text,
                                    "text": "Your piano homework%s: open the link and play on Doremi Road." %
                                            (" from " + who if who else "")})
        except Exception as e:
            if "Abort" not in type(e).__name__ + str(e):
                self.copy_button_click()

    @handle("retry_button", "click")
    def retry_button_click(self, **event_args):
        game.reset()
        router.go("teacher")

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(False)
