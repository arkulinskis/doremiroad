from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import StageTemplate
from ... import dr


class Stage(StageTemplate):
    """A level in the level engine (dr-engine.js DR.Stage). The engine draws everything inside; this component turns
    its callbacks into Anvil events (paused / finished / failed) and stops it when the page goes away."""

    def __init__(self, **properties):
        self._stage = None
        super().__init__(**properties)

    def start(self, level, subtitle="", skin="classic", trail="lantern"):
        self.destroy()
        opts = dr.js({"skin": skin, "trail": trail, "subtitle": subtitle})
        opts.onPause = anvil.js.report_exceptions(lambda *a: self.raise_event("paused"))
        opts.onFinish = anvil.js.report_exceptions(self._finish)
        opts.onFail = anvil.js.report_exceptions(self._fail)
        self._stage = window.DR.Stage(self.dom_nodes["host"], dr.js(level), opts)
        self._stage.start()

    def _finish(self, result, acc=None, *rest):
        self.raise_event("finished", result=dr.py(result), accuracy=float(acc or 0))

    def _fail(self, info, *rest):
        self.raise_event("failed", info=dr.py(info) or {})

    def running(self):
        return self._stage is not None

    def pause(self):
        if self._stage is not None:
            self._stage.pause()

    def resume(self):
        if self._stage is not None:
            self._stage.resume()

    def is_paused(self):
        return bool(self._stage is not None and self._stage.isPaused())

    def is_over(self):
        return bool(self._stage is None or dr.py(self._stage.state()).get("over"))

    def relabel(self):
        if self._stage is not None:
            self._stage.keyboard.relabel()

    def skip(self):
        """Tests: jump to the next step."""
        if self._stage is not None:
            self._stage.skip()

    def destroy(self):
        if self._stage is not None:
            try:
                self._stage.destroy()
            except Exception:
                pass
            self._stage = None

    @handle("", "hide")
    def form_hide(self, **event_args):
        self.destroy()
