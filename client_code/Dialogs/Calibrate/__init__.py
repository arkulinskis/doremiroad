from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import CalibrateTemplate
from ... import dr, state


def _loose(x):
    return x


class Calibrate(CalibrateTemplate):
    """Settings > Timing > Calibrate: the tap-with-the-beat test (dr-ui.js DR.UI.calibrate). It measures how late the
    player's taps land (Bluetooth speakers, TVs) and closes with that many milliseconds (0-300), or None."""

    def __init__(self, current=0, **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 2)
        state.live(self.status_label)
        self._api = _loose(None)
        self._ms = 0
        self.status_label.text = "Your timing now: %d ms." % int(current or 0)
        self.save_button.visible = False

    def _stop(self):
        if self._api is not None:
            try:
                self._api.stop()
            except Exception:
                pass
            self._api = None

    @handle("start_button", "click")
    def start_button_click(self, **event_args):
        self._stop()
        self.save_button.visible = False
        self.start_button.visible = False
        self.status_label.text = "Listen for four clicks, then tap on the next eight."
        opts = dr.js({})
        opts.onTap = anvil.js.report_exceptions(self._tap)
        opts.onDone = anvil.js.report_exceptions(self._done)
        pad = self.dom_nodes["pad"]
        self._api = window.DR.UI.calibrate(pad, opts)
        getattr(pad, "focus")()

    def _tap(self, n, of, *rest):
        self.status_label.text = "Tap %d of %d" % (n, of)

    def _done(self, ms, taps, *rest):
        self.start_button.visible = True
        self.start_button.text = "Try again"
        if ms is None:
            self.status_label.text = ("Only %d taps landed near a dot. Try again: tap as each dot touches the line."
                                      % int(taps or 0))
            return
        self._ms = int(ms)
        self.save_button.visible = True
        if self._ms <= 10:
            self.status_label.text = "Spot on: your taps land right on the beat. Save keeps the timing at %d ms." % self._ms
        else:
            self.status_label.text = ("Your taps land about %d ms late. Save it and rushes will take that off every note."
                                      % self._ms)
        state.focus(self.save_button)

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        dr.sfx("click")
        self._stop()
        self.raise_event("x-close-alert", value=self._ms)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self._stop()
        self.raise_event("x-close-alert", value=None)

    @handle("", "hide")
    def form_hide(self, **event_args):
        self._stop()
