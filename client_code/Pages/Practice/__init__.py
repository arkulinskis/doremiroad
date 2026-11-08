from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import PracticeTemplate
from ... import dr, game, state

SHOWS = [("Nothing", "none"), ("Major scale", "major"), ("Natural minor", "minor"), ("Harmonic minor", "harmonic"),
         ("Major pentatonic", "penta"), ("Minor pentatonic", "mpenta"), ("Blues scale", "blues"), ("Dorian", "dorian"),
         ("Mixolydian", "mixolydian"), ("A chord", "chord")]
KEYS = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


class Practice(PracticeTemplate):
    """#practice (Operate): play freely and every chord is named; light up a scale or chord; a metronome.
    The keyboard and the naming are the engine (Components/Keys -> DR.UI.practice); the tools are Forms."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        game.ensure()  # the header's rank and ducats, and the equipped keyboard skin
        ps = dr.store_get("dr.practice", None) or {}
        self._ps = {"show": ps.get("show") or "none", "key": ps.get("key") or "C", "chord": ps.get("chord") or "Cmaj7",
                    "bpm": int(ps.get("bpm") or 90), "lo": ps.get("lo")}
        self.show_drop.items = SHOWS
        self.show_drop.selected_value = self._ps["show"] if self._ps["show"] in [v for _, v in SHOWS] else "none"
        self.key_drop.items = KEYS
        self.key_drop.selected_value = self._ps["key"] if self._ps["key"] in KEYS else "C"
        self.chord_box.text = self._ps["chord"]
        bpm = self.dom_nodes["bpm"]
        window.Object.assign(bpm, {"value": str(self._ps["bpm"])})
        bpm.addEventListener("input", anvil.js.report_exceptions(self._bpm))
        self.bpm_label.text = str(self._ps["bpm"])
        state.set_control_attr(self.show_drop, "aria-label", "What to show on the keys")
        state.set_control_attr(self.key_drop, "aria-label", "Key")
        state.set_control_attr(self.chord_box, "aria-label", "Chord to show")
        state.set_control_attr(self.chord_box, "spellcheck", "false")
        state.set_control_attr(self.down_button, "aria-label", "Lower octave")
        state.set_control_attr(self.up_button, "aria-label", "Higher octave")
        state.live(self.chord_label)
        self._fields()
        self._api = None

    def _fields(self):
        show = self._ps["show"]
        self.key_field.visible = show not in ("chord", "none")
        self.chord_field.visible = show == "chord"

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(False)
        ps = dict(self._ps)
        if game.ready():
            ps["skin"] = game.S["progress"]["equip"].get("skins") or "classic"
        self._api = self.keys.practice(ps, self._chord, self._info, self._range)

    def leave(self):
        self.keys.stop()
        self._api = None

    # ---- engine callbacks
    def _chord(self, big, small):
        self.chord_label.text = big
        self.notes_label.text = small

    def _info(self, text, midi_link):
        self.info_label.text = text
        self.midi_button.visible = bool(midi_link)

    def _range(self, text, can_down, can_up):
        self.range_label.text = text
        self.down_button.enabled = bool(can_down)
        self.up_button.enabled = bool(can_up)

    # ---- tools
    def _set(self, k, v):
        self._ps[k] = v
        if self._api is not None:
            self._api.set(k, v)

    @handle("show_drop", "change")
    def show_drop_change(self, **event_args):
        self._set("show", self.show_drop.selected_value)
        self._fields()

    @handle("key_drop", "change")
    def key_drop_change(self, **event_args):
        self._set("key", self.key_drop.selected_value)

    @handle("chord_box", "change")
    def chord_box_change(self, **event_args):
        self._set("chord", self.chord_box.text or "")

    def _bpm(self, event):
        v = int(float(getattr(self.dom_nodes["bpm"], "value") or 90))
        self.bpm_label.text = str(v)
        self._set("bpm", v)

    @handle("hear_button", "click")
    def hear_button_click(self, **event_args):
        self.keys.hear()

    @handle("metro_button", "click")
    def metro_button_click(self, **event_args):
        if self._api is not None:
            on = bool(self._api.metro())
            self.metro_button.text = "Stop" if on else "Start"

    @handle("down_button", "click")
    def down_button_click(self, **event_args):
        if self._api is not None:
            dr.sfx("click")
            self._api.oct(-1)

    @handle("up_button", "click")
    def up_button_click(self, **event_args):
        if self._api is not None:
            dr.sfx("click")
            self._api.oct(1)

    @handle("midi_button", "click")
    def midi_button_click(self, **event_args):
        if self._api is not None:
            self._api.midi()
