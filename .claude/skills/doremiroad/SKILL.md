---
name: doremiroad
description: Context, workflow and recipes for Doremi Road (folder doremiroad-forms), the user's Anvil piano-learning game built as native Anvil Forms (Python + HTML templates, a layout, custom components, RepeatingPanels) around JavaScript engines (synth, MIDI/keys/touch input, the Stage, map art). A road across a knowledge map of music theory with an #admin level editor. Load this before any feature request, bug fix, new level/territory/collectable, restyle or deploy for this app.
---

# Doremi Road: working on the game

**What it is:** a piano-learning game. 9 territories × 4-5 levels (42) on a knowledge map; levels are lists of steps
(lesson, notes, chords, progression, rush, ear, quiz). Collectables: codex pages, composer cards, crests, badges,
ranks, shop skins/trails/banners, daily practice streaks. Guest play + accounts, leaderboards, Practice Room, level
editor at `#admin`. Aimed a bit older than Busy Bun (teens/adults).

**Where it lives:**
- Folder `C:\Users\arkvi\Documents\CLAUDE\doremiroad-forms\` = the git clone of **github.com/arkulinskis/doremiroad**,
  branch `master`. "git" layout: the folder *is* the Anvil app. Anvil pulls master; pushing is the deploy.
  Live: https://doremiroad.com.
- Native Forms since 2026-11-08 (forms branch merged that day). The old source folder `..\doremiroad` is retired
  (RETIRED.md; its deploy.py refuses to run): never deploy from it.
- Made like `APP_MAKER\template-forms`; its guide has the general Forms patterns, accessibility and design-kit rules.
- **README.md** lists every feature. **APP_MAP.md** is the code map: read it first, regenerate after changes
  (`python -I C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/standard/app_map.py doremiroad`).

**What the user wants:** a serious-enough game that teaches piano and basic theory, lots to collect, many levels, MIDI
or computer keyboard or touch, progressions and Guitar-Hero-style rush challenges, badges and territory conquest,
admin-editable levels. Dark navy + gold, serif titles; **dark only** (no light theme). Claude assumes and builds;
Claude deploys. Every page fits 390 px.

## Workflow for any change

1. `git pull --ff-only` (Anvil commits "Edited ..." when the user changes something in the IDE).
2. Edit a page's template and Python side by side (`client_code/Pages/X/`), or an engine in `theme/assets/dr-*.js`.
3. `python tools/check.py` (no -I) -> **ALL CHECKS PASSED**: `anvil validate`, `node --check` on the engines, asset
   hashes (`tools/assets.py`), server tests, and the music parity test (Music.py vs dr-music.js).
4. `python -I tools/ui_test.py` (Docker Desktop running) -> the smoke test (tools/ui/smoke.js: every address signed
   out / member / admin, desktop + phone). Server edits need `--restart`; `--stop` at the end.
5. Commit as arkulinskis with the Co-Authored-By line; `git push origin master`. New tables/columns: tell the user to
   accept the **Schema Mismatch** alert ("The schema of the source code is correct"). Regenerate APP_MAP.md.

## Architecture

```
client_code/
  startup.py, router.py, state.py, auth.py, legal.py   as template-forms (legal.py = the kit: don't edit)
  dr.py          the ONLY way Python reaches the engines (window.DR.*)
  game.py        game state: game.S, guest progress in localStorage `dr.guest`, guest_* server twins,
                 signed_in() -> import_guest
  Layouts/Shell  header (hidden on #landing: no-header; everything hidden on #play: no-chrome), footer (4 links)
  Pages/         Landing, Map, Codex, Collection, Practice, Badges, Shop, Play (#play/<key>, #play/daily), Auth, Admin
  Components/    Stage (the level runner), Keys (piano), KnowledgeMap, Art, TitleScene, SettingsPanel
  Items/         level/step/badge/shop/codex/composer tiles, board + admin rows
  Dialogs/       Results, Pause, Fail (opened from the Stage's events), LevelCard, DailyCard, CodexPage,
                 ComposerView, Profile, Settings, LevelJson
server_code/     Game.py (apply_* rules + callables + guest_* twins), Levels.py (built-in levels, check, _step_items),
                 Music.py, Catalog.py, Admin.py, Accounts.py, SchemaCheck, legal_server, seo_routes
theme/assets/    dr-core.js (DR.Sound synth, DR.Input = MIDI + computer keys + touch, DR.settings), dr-music.js
                 (theory; must match Music.py), dr-art.js (map, crests, medallions, title scene), dr-engine.js
                 (DR.Keyboard, DR.Stage: every step type, scoring, rush highway), dr-ui.js (Practice Room engine
                 DR.UI.practice, codex example keyboard, shop previews, DR.Admin = editor checks/previews/hear),
                 ark-music.js (shared player, generated), app.css, app-kit.js, theme.css
```

## How things are done here

- Pages, lists, dialogs, buttons, server calls: the template-forms patterns (its guide).
- Every progress rule is an `apply_*(progress, ...)` in Game.py with a signed-in callable and a `guest_*` twin.
- Scored items per step: `Levels._step_items` (server) == `stepItems` in dr-engine.js. The server rejects a result
  whose `items` differs. Result checking stays on the server.
- Music parsing lives twice: `server_code/Music.py` and `dr-music.js` (`tools/testing/music_parity.py` compares them).
  Level checks live twice: `Levels.check` and `DR.Admin` in dr-ui.js.
- Input: `DR.Input` merges MIDI, computer keys (only while something calls `DR.Input.capture(true)`) and on-screen
  keys. Sound is synthesized (`DR.Sound`).
- Touch piano: `DR.touchUI()` (settings.touch auto/on/off; auto = `(pointer: coarse)`), `<html class="dr-touch">`.
  Style touch-only things under `.dr-touch`; text that mentions computer keys or Enter checks `DR.touchUI()`.
  `DR.applyTouch()` re-emits Input's `'base'` event so keyboards and hint lines redraw. `DR.Keyboard` tracks one key
  per pointerId (multi-finger chords, slides).
- Built-in levels are Python in Levels.py (helpers `lesson/notes/chords/prog/rush/ear/quiz`), seeded only when missing.

## Recipes

- **New codex page / composer / badge / shop item:** Catalog.py (badge test in `Game.check_badges` unless it's a
  `stat`+`at` badge). A codex page or card must be given by exactly one level (server test).
- **New step type:** Levels (`STEP_TYPES`, `_step_items`, `check`), Admin `_clean_step`, dr-engine.js runner +
  `stepItems`, DR.Admin checks/fields in dr-ui.js and the Admin page, Art step icons/names.
- **New chord quality:** CHORD_TYPES in both Music.py and dr-music.js (+ parity inputs).
- **New page:** template-forms recipe; add its address to tools/ui/smoke.js.

## Gotchas

- A `role` on a custom HTML-form component (Keys, Art) is not applied on the App Server: wrap it in a div with a class.
- The --c-* tokens are the old --dr-* palette; the engines still read --dr-*: keep both.
- Continue with Google: `login_with_google()` returns None for someone without an account, so the code then calls
  `signup_with_google()`; on sign-up it needs the Privacy & Terms tick first. Sign-in is the #auth page.
- Web MIDI needs Chrome/Edge and a permission prompt; ask only on a click ("Connect"), then reconnect silently. No
  Web MIDI on iPhone/iPad: there only the touch piano shows.
- Test fingers with `new PointerEvent('pointerdown', {pointerId, pointerType: 'touch', clientX, clientY, bubbles: true})`;
  a slide is a `pointermove` on the first key with the second key's coordinates.
- Never write Anvil's theme-colour token pattern (percent, `color:`, name, percent) in theme.css.

## Music

Map music in `Sound.ambient` (dr-core.js); `Sound.setVolume` also sets the music volume; synth chords are the
fallback. Player = `window.ArkMusic` in theme/assets/ark-music.js, written by `APP_MAKER/tools/music_sync.py`: edit
`APP_MAKER/media/public/ark-music.js` and re-sync, never the copy. Tracks: `APP_MAKER/media/manifest.json`.

## Privacy & Terms (legal kit)

From `C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/legal-kit` (`apps/doremiroad.json`): `python -I build.py doremiroad &&
python -I install.py doremiroad` there (writes theme/assets/legal-kit.js, client_code/legal.py,
server_code/legal_server.py, the head_html tag), then `python tools/assets.py` and deploy. Sign-up keeps the tick box
(Pages/Auth). Consent is stored in `users.legal_version`, `legal_accepted_at`, `legal_source`. Feedback = Prepsto
only ("Submit feedback").
