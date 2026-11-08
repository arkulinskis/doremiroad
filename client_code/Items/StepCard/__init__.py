import json
import re

from anvil import *
from anvil.js import window

from ._anvil_designer import StepCardTemplate
from ... import dr, state

HEARABLE = ("rush", "lesson", "notes", "chords", "progression")
EAR_DEFAULT = {"note": ["C4", "E4", "G4"], "chord": ["major", "minor"], "interval": ["M3", "P5"]}


def _words(v):
    return [x for x in re.split(r"[\s,]+", v or "") if x]


def _lines(v):
    out = [x.strip() for x in (v or "").split("\n")]
    while out and not out[-1]:
        out.pop()
    return out


def _int(v):
    try:
        return int(float(v))
    except Exception:
        return 0


class StepCard(StepCardTemplate):
    """One step of a level in the editor: item = {s (the step dict, edited in place), i, collapsed, host}.
    Only the fields of the step's kind are shown (the same fields the JavaScript editor had). Every change updates
    the summary and preview here and calls host.dirty() (which re-runs the checks)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        s, i = self.item["s"], self.item["i"]
        t = s.get("t")
        self._t = t
        self.num_label.text = str(i + 1)
        self.kind_label.text = "%s %s" % (dr.step_icon(t), dr.step_name(t))
        state.heading(self.kind_label, 3)
        self.hear_button.visible = t in HEARABLE
        col = self.item["collapsed"]
        self.body.visible = not col
        self.fold_button.text = "▸" if col else "▾"
        for b, what in ((self.hear_button, "Hear step"), (self.up_button, "Move step up"), (self.down_button, "Move step down"),
                        (self.dup_button, "Duplicate step"), (self.fold_button, "Fold step"), (self.del_button, "Delete step")):
            state.set_control_attr(b, "aria-label", "%s %d" % (what, i + 1))
        # which fields this kind of step has
        vis = {
            "prompt_f": t not in ("lesson", "quiz"), "title_f": t == "lesson", "text_f": t == "lesson", "lesson_row": t == "lesson",
            "notes_f": t == "notes", "chords_f": t == "chords", "labels_f": t in ("notes", "chords"), "prog_row": t == "progression",
            "seq_f": t == "rush", "showmode_f": t == "notes", "clef_f": t == "notes", "mode_f": t == "ear", "bpm_f": t == "rush",
            "count_f": t == "ear", "pool_f": t == "ear" and s.get("mode") == "note",
            "poolchips_f": t == "ear" and s.get("mode") in ("chord", "interval"), "quiz_f": t == "quiz",
            "opts_row": t in ("notes", "chords", "progression", "rush", "ear"),
        }
        for name, on in vis.items():
            getattr(self, name).visible = on
        self.hint_box.visible = t in ("chords", "progression", "rush")
        self.hint_box.text = "Names on the falling notes" if t == "rush" else "Light up the keys"
        self.names_box.visible = t == "progression"
        self.exact_box.visible = t in ("notes", "chords", "rush")
        self.exact_box.text = "Exact notes and octave" if t == "chords" else "Exact octave"
        # values
        self.prompt_box.text = s.get("prompt") or ""
        self.title_box.text = s.get("title") or ""
        self.text_box.text = s.get("text") or ""
        self.show_box.text = " ".join(s.get("show") or []) if t == "lesson" else ""
        self.staff_drop.items = [("No", ""), ("Treble clef", "treble"), ("Bass clef", "bass")]
        self.staff_drop.selected_value = s.get("staff") or ""
        self.notes_box.text = " ".join(s.get("notes") or [])
        self.chords_box.text = " ".join(s.get("chords") or [])
        self.labels_box.text = "\n".join(s.get("labels") or [])
        self.key_box.text = s.get("key") or ""
        self.numerals_box.text = " ".join(s.get("numerals") or [])
        self.seq_box.text = s.get("seq") or ""
        self.showmode_drop.items = [("Lit keys (easiest)", "keys"), ("Note names", "names"), ("A staff (reading)", "staff")]
        self.showmode_drop.selected_value = s.get("show") if t == "notes" and s.get("show") in ("keys", "names", "staff") else "keys"
        self.clef_drop.items = [("Treble", "treble"), ("Bass", "bass")]
        self.clef_drop.selected_value = s.get("clef") if s.get("clef") in ("treble", "bass") else "treble"
        self.mode_drop.items = [("A note (player plays it)", "note"), ("A chord (pick its kind)", "chord"),
                                ("Two notes (pick the interval)", "interval")]
        self.mode_drop.selected_value = s.get("mode") if s.get("mode") in ("note", "chord", "interval") else "note"
        self.bpm_box.text = str(s.get("bpm") if s.get("bpm") is not None else "")
        self.count_box.text = str(s.get("count") if s.get("count") is not None else "")
        self.hint_box.checked = bool(s.get("hint"))
        self.names_box.checked = bool(s.get("names"))
        self.exact_box.checked = bool(s.get("exact"))
        self.pool_box.text = " ".join(s.get("pool") or []) if s.get("mode") == "note" else ""
        if vis["poolchips_f"]:
            self._draw_pool()
        self.q_box.text = s.get("q") or ""
        opts = s.get("options") or []
        for j in range(6):
            rb = getattr(self, "ans%d" % j)
            rb.group_name = "ans-%d-%d" % (i, id(self) % 100000)
            rb.selected = (s.get("answer") or 0) == j
            state.set_control_attr(rb, "aria-label", "Answer %d is the right one" % (j + 1))
            rb.add_event_handler("clicked", self._make_answer(j))
            box = getattr(self, "opt%d" % j)
            box.text = opts[j] if j < len(opts) else ""
            state.set_control_attr(box, "aria-label", "Answer %d" % (j + 1))
            box.add_event_handler("change", self._options)
        self.explain_box.text = s.get("explain") or ""
        # change handlers
        for name in ("prompt", "title", "text", "show", "notes", "chords", "labels", "key", "numerals", "seq", "bpm", "count",
                     "pool", "q", "explain"):
            getattr(self, name + "_box").add_event_handler("change", self._field)
        for c in (self.staff_drop, self.showmode_drop, self.clef_drop, self.hint_box, self.names_box, self.exact_box):
            c.add_event_handler("change", self._field)
        self.mode_drop.add_event_handler("change", self._mode)
        self._show()

    # ---- reading the fields back into the step
    def _field(self, **event_args):
        s, t = self.item["s"], self._t
        if t != "lesson" and t != "quiz":
            s["prompt"] = self.prompt_box.text or ""
        if t == "lesson":
            s["title"] = self.title_box.text or ""
            s["text"] = self.text_box.text or ""
            s["show"] = _words(self.show_box.text)
            s["staff"] = self.staff_drop.selected_value or None
        elif t == "notes":
            s["notes"] = _words(self.notes_box.text)
            s["labels"] = _lines(self.labels_box.text)
            s["show"] = self.showmode_drop.selected_value
            s["clef"] = self.clef_drop.selected_value
            s["exact"] = bool(self.exact_box.checked)
        elif t == "chords":
            s["chords"] = _words(self.chords_box.text)
            s["labels"] = _lines(self.labels_box.text)
            s["hint"] = bool(self.hint_box.checked)
            s["exact"] = bool(self.exact_box.checked)
        elif t == "progression":
            s["key"] = (self.key_box.text or "").strip()
            s["numerals"] = _words(self.numerals_box.text)
            s["hint"] = bool(self.hint_box.checked)
            s["names"] = bool(self.names_box.checked)
        elif t == "rush":
            s["seq"] = self.seq_box.text or ""
            s["bpm"] = _int(self.bpm_box.text)
            s["hint"] = bool(self.hint_box.checked)
            s["exact"] = bool(self.exact_box.checked)
        elif t == "ear":
            s["count"] = _int(self.count_box.text)
            if s.get("mode") == "note":
                s["pool"] = _words(self.pool_box.text)
        elif t == "quiz":
            s["q"] = self.q_box.text or ""
            s["explain"] = self.explain_box.text or ""
        self._show()
        self.item["host"].dirty()

    def _options(self, **event_args):
        s = self.item["s"]
        opts = [getattr(self, "opt%d" % j).text or "" for j in range(6)]
        while opts and not opts[-1].strip():
            opts.pop()
        s["options"] = opts
        self._show()
        self.item["host"].dirty()

    def _make_answer(self, j):
        def handler(**event_args):
            self.item["s"]["answer"] = j
            self.item["host"].dirty()
        return handler

    def _mode(self, **event_args):
        s = self.item["s"]
        s["mode"] = self.mode_drop.selected_value
        s["pool"] = list(EAR_DEFAULT[s["mode"]])
        self.item["host"].step_redraw()

    def _draw_pool(self):
        s = self.item["s"]
        choices = json.loads(window.DR.Admin.earChoices(s.get("mode")))
        pool = s.get("pool") or []
        self.pool_panel.items = [{"label": label, "key": v, "kind": "pool", "on": v in pool, "host": self} for v, label in choices]

    def chip_clicked(self, kind, key):
        """An ear-question answer chip (chord kinds or intervals)."""
        s = self.item["s"]
        s["pool"] = s.get("pool") or []
        if key in s["pool"]:
            s["pool"].remove(key)
        else:
            s["pool"].append(key)
        self._draw_pool()
        self._show()
        self.item["host"].dirty()

    def _show(self):
        s = json.dumps(self.item["s"])
        self.summary_label.text = str(window.DR.Admin.summary(s))
        pv = str(window.DR.Admin.preview(s))
        self.preview_label.text = pv
        self.preview_label.visible = bool(pv)

    def set_bad(self, bad):
        self.card.classes["bad"] = bool(bad)

    # ---- header buttons
    def _act(self, what):
        self.item["host"].step_action(self.item["i"], what)

    @handle("hear_button", "click")
    def hear_button_click(self, **event_args):
        self._act("hear")

    @handle("up_button", "click")
    def up_button_click(self, **event_args):
        self._act("up")

    @handle("down_button", "click")
    def down_button_click(self, **event_args):
        self._act("down")

    @handle("dup_button", "click")
    def dup_button_click(self, **event_args):
        self._act("dup")

    @handle("fold_button", "click")
    def fold_button_click(self, **event_args):
        self._act("fold")

    @handle("del_button", "click")
    def del_button_click(self, **event_args):
        self._act("del")
