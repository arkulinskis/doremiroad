from anvil import *

from ._anvil_designer import SongsTemplate
from ... import dr, game, router, state


class Songs(SongsTemplate):
    """#songs (Operate): the Song Shelf. Public-domain songs on two shelves (Christmas, Favourites), all open from the
    start, guests too. Each card (Items/SongCard) links to #play/song/<key>/<learn|practice|perform>."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title_label, 1)
        self._draw()

    def _draw(self):
        ok = game.ensure() and bool(game.S["songs"]["songs"])
        self.shelves_box.visible = ok
        self.failed_box.visible = not ok
        if not ok:
            return
        songs = game.S["songs"]["songs"]
        xmas = [s for s in songs if s["shelf"] == "christmas"]
        fav = [s for s in songs if s["shelf"] != "christmas"]
        self.xmas_panel.items = xmas
        self.fav_panel.items = fav
        stars = 0
        for s in songs:
            stars += sum(game.song_stars(s["key"]).values())
        done = len(game.songs_performed())
        self.lede_label.text = ("%d songs, open from the very first minute. %s of %d stars collected%s." % (
            len(songs), dr.fmt(stars), 3 * 3 * len(songs),
            ", %d performed" % done if done else ""))
        self.xmas_count.text = self._count(xmas)
        self.fav_count.text = self._count(fav)

    def _count(self, songs):
        done = len([s for s in songs if game.song_stars(s["key"])["perform"]])
        return "%d songs · %d performed" % (len(songs), done)

    @handle("retry_button", "click")
    def retry_button_click(self, **event_args):
        game.reset()
        self._draw()
        router.refresh_shell()

    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(False)  # quiet, so "Hear it" can be heard

    def leave(self):
        dr.stop_preview()
