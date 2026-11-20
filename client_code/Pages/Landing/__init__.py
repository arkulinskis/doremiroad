from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import LandingTemplate
from ... import auth, dr, game, homework, router, state

# The app's video on the Addanapp YouTube channel (APP_MAKER/youtube/manifest.json), shown in the Watch section.
YT_VIDEO = "RXNcbqR-jRs"


class Landing(LandingTemplate):
    """The title screen ("" and #landing; Persuade): the night road (Components/TitleScene), Begin / Continue, how you
    can play (MIDI, keys, touch), then the Watch section (the YouTube video) and How to play."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self._off = None
        self._jump = args[0] if args and args[0] in ("how", "watch") else None
        self.dom_nodes["yt_cover"].addEventListener("click", anvil.js.report_exceptions(self._play))
        self._draw()

    def _draw(self):
        me = state.me()
        self.begin_button.visible = not me
        self.signin_button.visible = not me
        self.continue_button.visible = bool(me)
        self.signout_button.visible = bool(me)
        self.signup_link.visible = not me
        # The Song Shelf's door: Jingle Bells in the Christmas season (Nov 15 - Jan 10), the shelf the rest of the year
        md = dr.today()[5:]
        self._xmas = md >= "11-15" or md <= "01-10"
        self.song_button.text = "🎄 Play Jingle Bells now" if self._xmas else "🎵 Play a song now"
        hw = homework.stored()
        self.hw_link.visible = hw is not None
        if hw is not None:
            self.hw_link.text = "📋 Homework from %s" % homework.teacher_name(hw["hw"])
            self.hw_link.url = "#hw"
            state.set_attr(self.hw_link, "target", None)
        self._midi()

    def _midi(self):
        """iPad/iPhone browsers have no Web MIDI: on a touch screen just offer the on-screen piano."""
        m = dr.midi()
        touch = dr.touch()
        unsupported = m["status"] == "unsupported"
        self.keys_pills.visible = not touch
        self.tap_pill.visible = touch
        self.tap_pill.text = "👆 Play on the on-screen piano: tap the keys" if unsupported else "👆 or tap the on-screen piano"
        text = dr.midi_text()
        self.midi_pill.text = "🎹 " + text if text else ""
        self.midi_pill.visible = bool(text) and not (unsupported and touch)
        self.midi_button.visible = not text

    @handle("", "show")
    def form_show(self, **event_args):
        self._off = dr.on_input(dr.report(lambda kind, *a: self._midi() if kind == "midi" else None))
        if self._jump:
            target = window.document.getElementById(self._jump)
            if target:
                window.setTimeout(dr.report(lambda: target.scrollIntoView({"block": "start"})), 60)

    def leave(self):
        if self._off is not None:
            self._off()
            self._off = None
        self.scene.stop()

    @handle("begin_button", "click")
    def begin_button_click(self, **event_args):
        dr.sfx("click")
        router.go("map")

    @handle("song_button", "click")
    def song_button_click(self, **event_args):
        dr.sfx("click")
        if self._xmas:
            router.go("play", "song", "jingle-bells", "learn")
        else:
            router.go("songs")

    @handle("continue_button", "click")
    def continue_button_click(self, **event_args):
        dr.sfx("click")
        router.go("map")

    @handle("signin_button", "click")
    def signin_button_click(self, **event_args):
        dr.sfx("click")
        router.go("auth")

    @handle("signout_button", "click")
    def signout_button_click(self, **event_args):
        dr.sfx("click")
        auth.sign_out()
        state.toast("Signed out. Your road waits for you.")
        self._draw()
        router.refresh_shell()

    @handle("midi_button", "click")
    def midi_button_click(self, **event_args):
        dr.sfx("click")
        dr.enable_midi(dr.report(self._midi))

    def jump_click(self, event):
        event.preventDefault()
        target = window.document.getElementById(event.currentTarget.getAttribute("data-to"))
        if target:
            target.scrollIntoView({"behavior": "smooth", "block": "start"})

    def _play(self, event):
        """Swap the video's cover for YouTube's player (privacy-enhanced); nothing loads from YouTube before this
        click. The map music pauses while it plays."""
        if window.get("ArkMusic"):
            window.ArkMusic.pause()
        self.dom_nodes["yt_frame"].innerHTML = (
            '<iframe src="https://www.youtube-nocookie.com/embed/' + YT_VIDEO + '?autoplay=1&rel=0&playsinline=1" '
            'title="Doremi Road video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen '
            'referrerpolicy="strict-origin-when-cross-origin"></iframe>')
