import copy
import json

from anvil import *
import anvil.js
import anvil.server
from anvil.js import window

from ._anvil_designer import AdminTemplate
from ... import auth, dr, router, state

TABS = ("levels", "territories", "players")


def _loose(x):
    """Item forms from get_components() (the validator only knows them as Component)."""
    return x


def _int(v, d):
    try:
        return int(float(v))
    except Exception:
        return d


class Admin(AdminTemplate):
    """#admin (Operate, admins only): the level editor. Levels (every territory's levels; edit name, territory,
    thresholds, cards, codex pages and the steps, with live checks that match the server's; Playtest runs the unsaved
    level in the real engine; JSON; Original), Territories (name, emoji, blurb, colour, map position with a live map
    preview, order) and Players (progress + admin rights). The checks, previews and "hear it" are dr-ui.js
    (DR.Admin); every save is checked again by the server (Admin.py)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.A: dict = {"state": None, "tab": args[0] if args and args[0] in TABS else "levels", "cur": None, "dirty": False,
                  "terr": None, "collapsed": {}}
        self._keys = anvil.js.report_exceptions(self._on_key)
        self._unload = anvil.js.report_exceptions(self._on_unload)
        self.terr_drop.add_event_handler("change", self._level_field)
        for box in (self.name_box, self.intro_box, self.pass_box, self.two_box, self.three_box):
            box.add_event_handler("change", self._level_field)
            box.add_event_handler("lost_focus", self._level_field)
        for c in (self.published_box, self.trial_box, self.card_clear_drop, self.card_three_drop):
            c.add_event_handler("change", self._level_field)
        for box in (self.t_name, self.t_emoji, self.t_blurb):
            box.add_event_handler("change", self._terr_field)
        self.t_published.add_event_handler("change", self._terr_field)
        self.dom_nodes["tx"].addEventListener("input", anvil.js.report_exceptions(self._terr_xy))
        self.dom_nodes["ty"].addEventListener("input", anvil.js.report_exceptions(self._terr_xy))
        self.pt_box.visible = False
        self.add_panel.items = [{"label": dr.step_icon(t) + " " + dr.step_name(t), "key": t, "kind": "add", "host": self}
                                for t in list(window.DR.Admin.STEP_TYPES)]
        self.who_label.text = "Loading…"
        if self._got(self._call("admin_state")):
            self._draw()

    # ---------------------------------------------------------------- server
    def _call(self, fn, *args):
        try:
            return anvil.server.call(fn, *args)
        except Exception as e:
            name = type(e).__name__
            state.toast(str(e) if name == "PermissionDenied" else "Something went wrong. Please try again.", "error")
            if name != "PermissionDenied":
                print("admin call %s failed: %r" % (fn, e))
            return None

    def _got(self, r):
        if not r:
            return r
        if r.get("ok") is False and not r.get("territories"):
            state.toast(r.get("error") or "Something went wrong.", "error")
            return None
        if r.get("error"):
            state.toast(r["error"], "error")
        if r.get("territories"):
            self.A["state"] = r
        if r.get("note"):
            state.toast(r["note"], "ok")
        return r

    def _all_levels(self):
        return [{"t": t, "l": l} for t in self.A["state"]["territories"] for l in t["levels"]]

    # ---------------------------------------------------------------- frame
    def _draw(self):
        A = self.A
        st = A["state"]
        if not st:
            return
        me = state.me() or {}
        self.who_label.text = "%s · %d players · %d clears" % (me.get("email") or "", st["stats"]["players"], st["stats"]["clears"])
        for name, el in (("levels", self.tab_levels), ("territories", self.tab_terr), ("players", self.tab_players)):
            el.classes["on"] = A["tab"] == name
        self.levels_tab.visible = A["tab"] == "levels"
        self.terr_tab.visible = A["tab"] == "territories"
        self.players_tab.visible = A["tab"] == "players"
        if A["tab"] == "levels":
            self._draw_levels()
        elif A["tab"] == "territories":
            self._draw_territories()
        else:
            self._draw_players()

    def _leave_ok(self):
        return not self.A["dirty"] or confirm("You have unsaved changes to this level. Leave without saving?",
                                              buttons=[("Stay", False), ("Leave without saving", True)])

    def tab_click(self, event):
        tab = str(event.currentTarget.getAttribute("data-tab"))
        if tab == self.A["tab"] or not self._leave_ok():
            return
        if self.A["tab"] == "levels":
            self.A["dirty"] = False
        self.A["tab"] = tab
        router.replace("admin", "" if tab == "levels" else tab)
        self._draw()

    @handle("signout_button", "click")
    def signout_button_click(self, **event_args):
        if not self._leave_ok():
            return
        self.A["dirty"] = False
        auth.sign_out()
        state.toast("Signed out.")
        router.go("landing")

    # ---------------------------------------------------------------- levels
    def _draw_levels(self):
        A = self.A
        cur_key = A["cur"]["key"] if A["cur"] else None
        self.side_panel.items = [{"t": t, "cur": cur_key, "host": self} for t in A["state"]["territories"]]
        self._draw_editor()

    def _reselect(self):
        A = self.A
        if not A["cur"] or not A["cur"].get("key") or A["dirty"]:
            return
        x = next((y for y in self._all_levels() if y["l"]["key"] == A["cur"]["key"]), None)
        if x:
            A["cur"] = self._cur_from(x)

    def _cur_from(self, x):
        return {"key": x["l"]["key"], "name": x["l"]["name"], "territory": x["t"]["key"], "published": x["l"]["published"],
                "builtin": x["l"]["builtin"], "data": copy.deepcopy(x["l"]["data"])}

    def edit(self, key):
        """Open a level in the editor (from the side list)."""
        if not self._leave_ok():
            return
        x = next((y for y in self._all_levels() if y["l"]["key"] == key), None)
        if not x:
            return
        self.A.update(cur=self._cur_from(x), dirty=False, collapsed={})
        self._draw_levels()

    def new_level(self, terr_key):
        if not self._leave_ok():
            return
        blank = lambda t: json.loads(window.DR.Admin.blank(t))
        self.A.update(cur={"key": None, "name": "New level", "territory": terr_key, "published": True, "builtin": False,
                           "data": {"intro": "", "steps": [blank("lesson"), blank("notes")], "pass": 60, "two": 80,
                                    "three": 95, "codex": [], "cards": {}, "trial": False}},
                      dirty=True, collapsed={})
        self._draw_levels()

    def move_level(self, key, step):
        if self._got(self._call("move_level", key, step)):
            self._reselect()
            self._draw_levels()

    @handle("restore_button", "click")
    def restore_button_click(self, **event_args):
        if self._got(self._call("restore_defaults")):
            self._reselect()
            self._draw_levels()

    def _draw_editor(self):
        A = self.A
        c = A["cur"]
        self.pick_box.visible = c is None
        self.editor.visible = c is not None
        if c is None:
            return
        d = c["data"]
        st = A["state"]
        cat = st["catalog"]
        self.ed_title.text = c["name"]
        state.heading(self.ed_title, 2)
        self.dirty_label.text = "● unsaved" if A["dirty"] else ""
        self.original_button.visible = bool(c["builtin"])
        self.delete_button.visible = bool(c["key"])
        self.name_box.text = c["name"]
        self.terr_drop.items = [(t["name"], t["key"]) for t in st["territories"]]
        self.terr_drop.selected_value = c["territory"]
        self.published_box.checked = bool(c["published"])
        self.trial_box.checked = bool(d.get("trial"))
        self.intro_box.text = d.get("intro") or ""
        self.pass_box.text = str(60 if d.get("pass") is None else d["pass"])
        self.two_box.text = str(80 if d.get("two") is None else d["two"])
        self.three_box.text = str(95 if d.get("three") is None else d["three"])
        cards = [("None", "")] + [("%s (%s)" % (x["name"], x["rarity"]), x["key"]) for x in cat["composers"]]
        self.card_clear_drop.items = cards
        self.card_three_drop.items = cards
        self.card_clear_drop.selected_value = (d.get("cards") or {}).get("clear") or ""
        self.card_three_drop.selected_value = (d.get("cards") or {}).get("three") or ""
        for box, label in ((self.terr_drop, "Territory"), (self.card_clear_drop, "Composer card for clearing"),
                           (self.card_three_drop, "Card for three stars")):
            state.set_control_attr(box, "aria-label", label)
        self._draw_codex()
        self._draw_steps()
        self._checks()

    def _draw_codex(self):
        c = self.A["cur"]
        used = {}
        for x in self._all_levels():
            if x["l"]["key"] != c["key"]:
                for k in x["l"]["data"].get("codex") or []:
                    used[k] = x["l"]["name"]
        have = c["data"].get("codex") or []
        self.codex_panel.items = [{"label": x["title"], "key": x["key"], "kind": "codex", "on": x["key"] in have,
                                   "used": x["key"] in used, "title": ("Also in " + used[x["key"]]) if x["key"] in used else x["text"],
                                   "host": self} for x in self.A["state"]["catalog"]["codex"]]

    def _draw_steps(self):
        steps = self.A["cur"]["data"]["steps"]
        self.steps_panel.items = [{"s": s, "i": i, "collapsed": bool(self.A["collapsed"].get(i)), "host": self}
                                  for i, s in enumerate(steps)]
        self.no_steps.visible = not steps

    def _level_field(self, **event_args):
        c = self.A["cur"]
        if c is None:
            return
        d = c["data"]
        c["name"] = self.name_box.text or ""
        c["territory"] = self.terr_drop.selected_value
        c["published"] = bool(self.published_box.checked)
        d["trial"] = bool(self.trial_box.checked)
        d["intro"] = self.intro_box.text or ""
        d["pass"] = _int(self.pass_box.text, 0)
        d["two"] = _int(self.two_box.text, 0)
        d["three"] = _int(self.three_box.text, 0)
        cards = {}
        for which, drop in (("clear", self.card_clear_drop), ("three", self.card_three_drop)):
            if drop.selected_value:
                cards[which] = drop.selected_value
        d["cards"] = cards
        self.ed_title.text = c["name"]
        self.dirty()

    def dirty(self):
        self.A["dirty"] = True
        self.dirty_label.text = "● unsaved"
        self._checks()

    def _checks(self):
        c = self.A["cur"]
        d = c["data"]
        errors, warnings, scored = json.loads(window.DR.Admin.check(json.dumps(d)))
        p = 60 if d.get("pass") is None else d["pass"]
        two = 80 if d.get("two") is None else d["two"]
        three = 95 if d.get("three") is None else d["three"]
        if not (p <= two <= three):
            errors.append("Star thresholds must go up: pass ≤ two stars ≤ three stars.")
        if d["steps"] and not scored:
            warnings.append("Nothing in this level is scored (only lessons): everyone gets three stars.")
        msgs = [{"kind": "e", "text": "✕ " + x} for x in errors] + [{"kind": "w", "text": "⚠ " + x} for x in warnings]
        if not msgs:
            msgs = [{"kind": "ok", "text": "✓ Ready to play: %d steps, %d scored items." % (len(d["steps"]), scored)}]
        if errors:
            msgs.append({"kind": "note", "text": "A level with errors is saved as a draft."})
        self.msgs_panel.items = msgs
        for comp in _loose(self.steps_panel.get_components()):
            i = comp.item["i"]
            comp.set_bad(any(x.startswith("Step %d:" % (i + 1)) for x in errors))
        return errors

    def chip_clicked(self, kind, key):
        """A codex chip (toggle the page) or an Add-a-step chip."""
        c = self.A["cur"]
        if c is None:
            return
        d = c["data"]
        if kind == "codex":
            d["codex"] = d.get("codex") or []
            if key in d["codex"]:
                d["codex"].remove(key)
            else:
                d["codex"].append(key)
            self._draw_codex()
            self.dirty()
        elif kind == "add":
            d["steps"].append(json.loads(window.DR.Admin.blank(key)))
            self._draw_steps()
            self.dirty()

    def step_action(self, i, what):
        steps = self.A["cur"]["data"]["steps"]
        s = steps[i]
        if what == "del":
            if not confirm("Delete step %d?" % (i + 1), buttons=[("Cancel", False), ("Delete", True)]):
                return
            steps.pop(i)
        elif what == "up" and i > 0:
            steps.insert(i - 1, steps.pop(i))
        elif what == "down" and i < len(steps) - 1:
            steps.insert(i + 1, steps.pop(i))
        elif what == "dup":
            steps.insert(i + 1, copy.deepcopy(s))
        elif what == "fold":
            self.A["collapsed"][i] = not self.A["collapsed"].get(i)
            self._draw_steps()
            self._checks()
            return
        elif what == "hear":
            window.DR.Admin.hear(json.dumps(s))
            return
        else:
            return
        self.A["collapsed"] = {}
        self._draw_steps()
        self.dirty()

    def step_redraw(self):
        """A step changed shape (an ear question's mode): redraw the step cards."""
        self._draw_steps()
        self.dirty()

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        self._level_field()
        c = self.A["cur"]
        r = self._got(self._call("save_level", {"key": c["key"], "name": c["name"], "territory": c["territory"],
                                                "published": c["published"], "data": c["data"]}))
        if r and r.get("saved"):
            self.A["dirty"] = False
            draft = bool(r.get("errors"))
            state.toast("Saved as a draft" if draft else "Saved", "error" if draft else "ok")
            x = next((y for y in self._all_levels() if y["l"]["key"] == r["saved"]), None)
            if x:
                self.A["cur"] = self._cur_from(x)
            self._draw_levels()

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        c = self.A["cur"]
        if confirm('Delete "%s"? Its scores are deleted too.' % c["name"], buttons=[("Cancel", False), ("Delete", True)]):
            if self._got(self._call("delete_level", c["key"])):
                self.A.update(cur=None, dirty=False)
                self._draw_levels()

    @handle("original_button", "click")
    def original_button_click(self, **event_args):
        c = self.A["cur"]
        if confirm('Put "%s" back to how it shipped? Your edits are lost.' % c["name"],
                   buttons=[("Cancel", False), ("Put it back", True)]):
            if self._got(self._call("restore_level", c["key"])):
                self.A["dirty"] = False
                key = c["key"]
                x = next((y for y in self._all_levels() if y["l"]["key"] == key), None)
                if x:
                    self.A["cur"] = self._cur_from(x)
                self._draw_levels()

    @handle("json_button", "click")
    def json_button_click(self, **event_args):
        from ...Dialogs.LevelJson import LevelJson
        d = alert(LevelJson(data=self.A["cur"]["data"]), buttons=[], large=True, role="app-dialog", dismissible=True)
        if isinstance(d, dict):
            self.A["cur"]["data"] = d
            self.A["dirty"] = True
            self._draw_editor()

    # ---- playtest: the unsaved level in the real engine
    @handle("playtest_button", "click")
    def playtest_button_click(self, **event_args):
        self._level_field()
        c = self.A["cur"]
        if self._checks():
            state.toast("Fix the errors first", "error")
            return
        t = next((x for x in self.A["state"]["territories"] if x["key"] == c["territory"]), None)
        self.pt_box.visible = True
        self.pt_stage.start({"name": c["name"], "data": copy.deepcopy(c["data"])}, "Playtest · " + (t["name"] if t else ""))

    def _end_pt(self):
        self.pt_stage.destroy()
        self.pt_box.visible = False

    @handle("end_pt_button", "click")
    def end_pt_button_click(self, **event_args):
        self._end_pt()

    @handle("pt_stage", "finished")
    def pt_stage_finished(self, result, accuracy, **event_args):
        self._end_pt()
        state.toast("Cleared with %d%% · %s items · score %s" % (round(accuracy), result.get("items"), result.get("score")), "ok")

    @handle("pt_stage", "failed")
    def pt_stage_failed(self, info, **event_args):
        self._end_pt()
        state.toast("Failed: the harmony meter ran out" if info.get("reason") == "meter"
                    else "Not cleared: %d%% accuracy" % round(info.get("accuracy") or 0), "error")

    # ---------------------------------------------------------------- territories
    def _draw_territories(self):
        A = self.A
        ts = A["state"]["territories"]
        if not A["terr"] or not any(t["key"] == A["terr"].get("key") for t in ts):
            if not (A["terr"] and A["terr"].get("key") is None):
                A["terr"] = copy.deepcopy(ts[0]) if ts else None
        cur = A["terr"]["key"] if A["terr"] else None
        self.terr_panel.items = [{"t": t, "on": t["key"] == cur, "host": self} for t in ts]
        self._terr_form()

    def _terr_form(self):
        t = self.A["terr"]
        self.terr_form.visible = t is not None
        self.no_terr.visible = t is None
        if t is None:
            return
        self.t_title.text = t.get("name") or "New territory"
        state.heading(self.t_title, 2)
        self.delt_button.visible = bool(t.get("key"))
        self.t_name.text = t.get("name") or ""
        self.t_emoji.text = t.get("emoji") or ""
        self.t_blurb.text = t.get("blurb") or ""
        self.t_published.checked = t.get("published") is not False
        self.colors_panel.items = [{"color": c, "on": t.get("color") == c, "host": self} for c in self.A["state"]["catalog"]["colors"]]
        for k, node, label in (("x", "tx", self.tx_label), ("y", "ty", self.ty_label)):
            window.Object.assign(self.dom_nodes[node], {"value": str(t.get(k) or 50)})
            label.text = str(int(round(t.get(k) or 50)))
        self._map_prev()

    def _map_prev(self):
        A = self.A
        t = A["terr"]
        ts = A["state"]["territories"]
        lst = [dict(x, **t) if x["key"] == t.get("key") else x for x in ts]
        if not t.get("key"):
            extra = dict(t)
            extra["levels"], extra["key"] = [], "_new"
            lst = lst + [extra]
        unlocked = [x["l"]["key"] for x in self._all_levels()] + ["_"]
        self.map_prev.content = dr.art_map(lst, {"unlocked": unlocked, "selected": t.get("key") or "_new", "current": t.get("key")})

    def pick_terr(self, key):
        t = next((x for x in self.A["state"]["territories"] if x["key"] == key), None)
        if t:
            self.A["terr"] = copy.deepcopy(t)
            self._draw_territories()

    def move_terr(self, key, step):
        if self._got(self._call("move_territory", key, step)):
            self._draw_territories()

    def pick_colour(self, color):
        self.A["terr"]["color"] = color
        for comp in _loose(self.colors_panel.get_components()):
            comp.set_on(comp.item["color"] == color)
        self._map_prev()

    @handle("new_terr_button", "click")
    def new_terr_button_click(self, **event_args):
        cols = self.A["state"]["catalog"]["colors"]
        ts = self.A["state"]["territories"]
        self.A["terr"] = {"key": None, "name": "New territory", "emoji": "🎵", "blurb": "", "color": cols[len(ts) % len(cols)],
                          "x": 50, "y": 50, "published": False, "levels": []}
        self.terr_panel.items = [{"t": t, "on": False, "host": self} for t in ts]
        self._terr_form()

    def _terr_field(self, **event_args):
        t = self.A["terr"]
        if t is None:
            return
        t["name"] = self.t_name.text or ""
        t["emoji"] = self.t_emoji.text or ""
        t["blurb"] = self.t_blurb.text or ""
        t["published"] = bool(self.t_published.checked)
        self.t_title.text = t["name"] or "New territory"
        self._map_prev()

    def _terr_xy(self, event):
        t = self.A["terr"]
        if t is None:
            return
        t["x"] = float(getattr(self.dom_nodes["tx"], "value"))
        t["y"] = float(getattr(self.dom_nodes["ty"], "value"))
        self.tx_label.text = str(int(round(t["x"])))
        self.ty_label.text = str(int(round(t["y"])))
        self._map_prev()

    @handle("savet_button", "click")
    def savet_button_click(self, **event_args):
        self._terr_field()
        t = self.A["terr"]
        spec = {k: t.get(k) for k in ("key", "name", "emoji", "blurb", "color", "x", "y", "published")}
        if self._got(self._call("save_territory", spec)):
            if not t.get("key"):
                nt = [x for x in self.A["state"]["territories"] if x["name"] == t["name"]]
                self.A["terr"] = copy.deepcopy(nt[-1]) if nt else None
            state.toast("Saved", "ok")
            self._draw_territories()

    @handle("delt_button", "click")
    def delt_button_click(self, **event_args):
        t = self.A["terr"]
        if confirm("Delete %s?" % t["name"], buttons=[("Cancel", False), ("Delete", True)]):
            r = self._got(self._call("delete_territory", t["key"]))
            if r and r.get("ok") is not False:
                self.A["terr"] = None
            self._draw_territories()

    # ---------------------------------------------------------------- players
    def _draw_players(self):
        self.players_note.text = "Loading…"
        self.players_note.visible = True
        r = self._call("list_players")
        if not r or not r.get("ok"):
            self._got(r)
            return
        self.players_panel.items = [{"p": p, "host": self, "me": (state.me() or {}).get("email")} for p in r["players"]]
        self.players_note.visible = not r["players"]
        self.players_note.text = "No players yet."

    def set_admin(self, email, flag):
        r = self._call("set_admin", email, flag)
        if not r or not r.get("ok"):
            state.toast((r or {}).get("error") or "Could not change that.", "error")
            return False
        state.toast("Saved", "ok")
        return True

    # ---------------------------------------------------------------- keys + leaving
    @handle("", "show")
    def form_show(self, **event_args):
        dr.ambient(False)
        window.addEventListener("keydown", self._keys)
        window.addEventListener("beforeunload", self._unload)

    def leave(self):
        window.removeEventListener("keydown", self._keys)
        window.removeEventListener("beforeunload", self._unload)
        self.pt_stage.destroy()

    def _on_key(self, event):
        if (getattr(event, "ctrlKey", False) or getattr(event, "metaKey", False)) and str(getattr(event, "key", None)).lower() == "s" and self.A["tab"] == "levels" and self.A["cur"]:
            event.preventDefault()
            self.save_button_click()

    def _on_unload(self, event):
        if self.A["dirty"]:
            event.preventDefault()
            event.returnValue = ""
