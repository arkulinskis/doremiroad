from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import SettingsPanelTemplate
from ... import dr, state

TOGGLES = [("sfx_box", "sfx", "Sound effects"), ("ambient_box", "ambient", "Ambient music on the map"),
           ("keysound_box", "keySound", "Piano sound for the on-screen and computer keys"),
           ("midisound_box", "midiSound", "Piano sound for MIDI keys"), ("metronome_box", "metronome", "Metronome during rushes"),
           ("letters_box", "letters", "Computer-key letters on the keys")]


class SettingsPanel(SettingsPanelTemplate):
    """The player's settings (DR.settings in this browser). Used in the profile dialog and the pause menu's Settings."""

    def __init__(self, **properties):
        super().__init__(**properties)
        for name, key, caption in TOGGLES:
            box = getattr(self, name)
            state.set_control_attr(box, "aria-label", caption)
            state.set_control_attr(box, "role", "switch")
            box.add_event_handler("change", self._make_toggle(box, key))
        vol = self.dom_nodes["volume"]
        vol.addEventListener("input", anvil.js.report_exceptions(self._volume))
        self._draw()

    def _make_toggle(self, box, key):
        def handler(**event_args):
            dr.set_setting(key, bool(box.checked))
            if key == "ambient":
                dr.ambient(bool(box.checked) and not window.location.hash.startswith("#play"))
            self.raise_event("changed")
        return handler

    def _draw(self):
        s = dr.settings()
        for name, key, caption in TOGGLES:
            getattr(self, name).checked = bool(s.get(key))
        touch = dr.touch()
        self.letters_caption.visible = not touch
        self.letters_box.visible = not touch
        for v, el in (("auto", self.touch_auto), ("on", self.touch_on), ("off", self.touch_off)):
            el.classes["on"] = s.get("touch", "auto") == v
        for v, el in (("none", self.labels_none), ("c", self.labels_c), ("all", self.labels_all)):
            el.classes["on"] = s.get("labels", "c") == v
        window.Object.assign(self.dom_nodes["volume"], {"value": str(s.get("volume", 0.8))})
        m = dr.midi()
        st = m["status"]
        self.midi_label.text = {"on": ", ".join(m["inputs"]),
                                "unsupported": "This browser has no Web MIDI. Use Chrome or Edge.",
                                "denied": "Blocked. Allow MIDI in the browser's site settings.",
                                "ready": "Allowed, but no keyboard found. Plug one in."}.get(st, "Not connected.")
        self.midi_button.visible = st not in ("on", "unsupported")

    def touch_click(self, event):
        dr.set_setting("touch", str(event.currentTarget.getAttribute("data-v")))
        dr.apply_touch()  # redraws keyboards and hint lines that are open
        self._draw()
        self.raise_event("changed")

    def labels_click(self, event):
        dr.set_setting("labels", str(event.currentTarget.getAttribute("data-v")))
        self._draw()
        self.raise_event("changed")

    def _volume(self, event):
        dr.set_volume(float(getattr(self.dom_nodes["volume"], "value") or 0.8))

    @handle("midi_button", "click")
    def midi_button_click(self, **event_args):
        dr.enable_midi(dr.report(self._draw))
