"""The bridge to Doremi Road's JavaScript engines (theme/assets/dr-*.js), so Forms never touch window.DR directly.

    dr.js(x) / dr.py(x)     Python data -> JS object, JS object -> Python data (always through JSON)
    dr.sfx(name)            a sound effect (click, page, coin, star, win, fail, card, conquer)
    dr.store_get/set/del    this browser's storage under the JavaScript version's keys (dr.guest, dr.practice ...)
    dr.settings() / set_setting(k, v)    the player's sound/keyboard settings (DR.settings, kept in this browser)
    dr.touch()              the touch-screen piano is on (tablets and phones, or the setting)
    dr.midi()               {status, inputs} of the MIDI connection; dr.enable_midi() asks the browser
    dr.art_*                SVG strings drawn by dr-art.js / dr-ui.js (map, crest, medallion, shop previews)
    dr.fmt(n)               1,234
"""
import json

import anvil.js
from anvil.js import window


def js(x):
    return window.JSON.parse(json.dumps(x))


def py(x):
    if x is None:
        return None
    s = window.JSON.stringify(x)
    return None if s is None else json.loads(s)


def DR():
    return window.DR


def sfx(name):
    try:
        window.DR.Sound.sfx(name)
    except Exception:
        pass


def ambient(on):
    try:
        window.DR.Sound.ambient(bool(on))
    except Exception:
        pass


def store_get(key, default=None):
    try:
        v = window.localStorage.getItem(key)
    except Exception:
        return default
    if v is None:
        return default
    try:
        return json.loads(v)
    except Exception:
        return default


def store_set(key, value):
    try:
        window.localStorage.setItem(key, json.dumps(value))
    except Exception:
        pass


def store_del(key):
    try:
        window.localStorage.removeItem(key)
    except Exception:
        pass


def today():
    return str(window.DR.today())


def fmt(n):
    try:
        return "{:,}".format(int(round(n or 0)))
    except Exception:
        return str(n)


def settings():
    return py(window.DR.settings) or {}


def set_setting(key, value):
    window.DR.settings[key] = value
    window.DR.saveSettings()


def set_volume(v):
    window.DR.Sound.setVolume(float(v))


def apply_touch():
    window.DR.applyTouch()


def touch():
    return bool(window.DR.touchUI())


def midi():
    m = py(window.DR.Input.midi) or {}
    return {"status": m.get("status") or "off", "inputs": m.get("inputs") or []}


def enable_midi(then=None):
    """Ask the browser for MIDI (only on a click). then() runs when the answer is in."""
    p = window.DR.Input.enableMidi(False)
    if then is not None:
        p.then(lambda *a: then())


def on_input(fn):
    """fn(kind, value) for every DR.Input event (midi, base, on, off). Returns a function that stops it."""
    return window.DR.Input.on(fn)


def midi_text(short=False):
    """What the MIDI pill says."""
    m = midi()
    st = m["status"]
    if st == "on":
        return "%s connected" % (m["inputs"][0] if m["inputs"] else "MIDI keyboard")
    if st == "unsupported":
        return "MIDI needs Chrome or Edge"
    if st == "denied":
        return "MIDI was blocked by the browser"
    if st == "ready":
        return "No MIDI keyboard found · plug one in"
    return ""


# ---------------------------------------------------------------- art (SVG strings from the engines)
def art_map(journey, opts):
    return str(window.DR.Art.map(js(journey), js(opts)))


def art_crest(terr, state, size):
    return str(window.DR.Art.crest(js(terr), state, size))


def art_medallion(card, have, size):
    return str(window.DR.Art.medallion(js(card), bool(have), size))


def shop_preview(kind, item):
    return str(window.DR.UI.shopPreview(kind, js(item)))


def step_icon(t):
    return str(window.DR.Art.STEP_ICONS[t] or "") if t else ""


def step_name(t):
    return str(window.DR.Art.STEP_NAMES[t] or t) if t else ""


def rarity_colour(r):
    return str(window.DR.Art.RARITY_COL[r] or "#e2b25a")


def level_items(data):
    return int(window.DR.Engine.levelItems(js(data)))


def pretty_notes(notes):
    """'C#4+E4' -> 'C♯4+E4' for each entry, joined with dots (the codex examples)."""
    M = window.DR.Music
    return "  ·  ".join("+".join(str(M.pretty(x)) for x in n.split("+")) for n in notes)


def report(fn):
    return anvil.js.report_exceptions(fn)
