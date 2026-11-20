from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import SongCardTemplate
from ... import dr, game, router

_now_playing = [None]  # the card whose "Hear it" is playing (one at a time)


class SongCard(SongCardTemplate):
    """A song on the Song Shelf: item = a song from game.S["songs"] (key, title, origin, level, bpm, seq, notes,
    seconds). Three ways to play it, each a link to #play/song/<key>/<mode> with its own stars, and "Hear it"."""

    def __init__(self, **properties):
        super().__init__(**properties)
        s = self.item
        stars = game.song_stars(s["key"])
        self.title_label.text = s["title"]
        self.origin_label.text = s["origin"]
        lv = int(s.get("level") or 1)
        self.dom_nodes["level"].textContent = "♪" * lv
        self.dom_nodes["level"].setAttribute("title", ["Easy", "Medium", "Harder"][lv - 1])
        self.dom_nodes["level"].setAttribute("aria-label", "Difficulty %d of 3" % lv)
        mins, secs = divmod(int(s.get("seconds") or 0), 60)
        self.dom_nodes["meta"].textContent = "%d notes · %d:%02d" % (s.get("notes") or 0, mins, secs)
        for m in game.SONG_MODES:
            link = self.dom_nodes["m_" + m]
            link.setAttribute("href", router.href("play", "song", s["key"], m))
            n = stars[m]
            self.dom_nodes["s_" + m].textContent = "★" * n + "☆" * (3 - n)
            link.classList.toggle("done", n > 0)
            link.setAttribute("aria-label", "%s %s, %s: %s" % (game.SONG_MODE_NAMES[m], s["title"], game.SONG_MODE_SUBS[m],
                                                               "%d of 3 stars" % n if n else "not played yet"))
        self.card.classes["perfect"] = all(stars[m] == 3 for m in game.SONG_MODES)
        self._playing = False
        self.dom_nodes["hear"].setAttribute("aria-label", "Hear how %s goes" % s["title"])
        self.dom_nodes["hear"].addEventListener("click", anvil.js.report_exceptions(self._hear))

    def _hear(self, event):
        if self._playing:
            dr.stop_preview()
            self._reset()
            return
        other = _now_playing[0]
        if other is not None and other is not self:
            other._reset()
        secs = dr.preview(self.item["seq"], self.item["bpm"], 16)
        if secs <= 0:
            return
        self._playing = True
        _now_playing[0] = self
        self.dom_nodes["hear"].textContent = "■ Stop"
        self.dom_nodes["hear"].classList.add("on")
        window.setTimeout(dr.report(self._ended), int(secs * 1000) + 300)

    def _ended(self):
        if _now_playing[0] is self and self._playing:
            self._reset()

    def _reset(self):
        self._playing = False
        if _now_playing[0] is self:
            _now_playing[0] = None
        self.dom_nodes["hear"].textContent = "♪ Hear it"
        self.dom_nodes["hear"].classList.remove("on")
