# Doremi Road

A piano-learning game for [anvil.works](https://anvil.works). You travel a road across the **Realm of Harmony**, a map of musical knowledge. Each territory teaches one part of music; every level you clear claims one of its provinces in your banner colour, and clearing them all conquers the territory and opens the next.

- **App repo:** github.com/arkulinskis/doremiroad (branch `master`). Anvil pulls `master`.
- **Level editor:** open the app with `#admin` at the end of the URL.

## Playing

Play with a **MIDI keyboard** (Web MIDI: Chrome or Edge), the **computer keyboard** (`Z`–`M` and `Q`–`U` are two octaves, black keys on the row above, `↑`/`↓` shift octave) or the **mouse/touch**. By default any octave counts; steps marked "exact" need the right octave.

**Challenge types** (a level is a list of steps):

| Step | What the player does |
|---|---|
| 📖 Lesson | Reads a short explanation; the keys (and optionally a staff) light up; "Hear it". Not scored. |
| 🎹 Notes | Plays notes in turn, shown as lit keys, names, labels ("a 5th above C") or on a treble/bass staff. |
| 🎼 Chords | Plays chords by symbol (C, Am, G7, Bdim…) or exact shapes (E4+G4+C5). Inversions count unless exact. |
| 🧭 Progression | Plays chords from Roman numerals in a key (I–V–vi–IV in G, ii7–V7–Imaj7 in B♭…). |
| ⚡ Rush | Guitar Hero style: notes and chords fall onto the keys in time. Perfect/great/good/miss, combo, a harmony meter that fails you if it empties. Count-in and metronome. |
| 👂 Ear | Hear a note and play it, or hear a chord/interval and pick its name. |
| ❓ Quiz | Multiple-choice theory question with an explanation. |

Accuracy across the level decides the result: 60% clears, 80% two stars, 95% three (the editor can change these per level).

## The road

9 territories, 42 levels: Ivory Shore (the keyboard, note names, octaves, first songs), Sharpwood (sharps and flats, half and whole steps), Major Highlands (major scales, intervals, pentatonic), Triad Vale (major and minor chords, inversions), Minor Marsh (minor scales, relative keys, diminished and augmented), Progression Pass (Roman numerals, cadences, pop/doo-wop/canon progressions), Staff Citadel (treble and bass clef reading, ledger lines), Blue Bayou (seventh chords, blues scale, twelve-bar blues, ii–V–I) and Circle Summit (circle of fifths, key signatures, modes, the final trial). Each territory ends in a Trial. Songs used are traditional or public domain (Ode to Joy, Für Elise, Greensleeves, Amazing Grace, Minuet in G…).

## Things to collect

1. **Provinces and territories** on the knowledge map, in your banner colour; a flag when conquered, a gold border when mastered (three stars everywhere).
2. **Codex**: 42 theory pages, each unlocked by the level that teaches it, with an example you can hear.
3. **Composer cards**: 20 (common → legendary), from first clears and three-star clears of certain levels, and as daily-practice drops. Duplicates sell for ducats.
4. **Territory crests**.
5. **32 badges**.
6. **Stars** (3 per level) and **ranks** by XP: Novice → Busker → Apprentice → Chorister → Accompanist → Soloist → Virtuoso → Maestro → Legend.
7. **Shop** (paid in ducats): 7 keyboard skins, 5 note trails for rushes, 7 map banners.
8. **Daily Practice**: a new generated level every day (harder as you conquer more), streak bonus, card chance.

Also: per-level leaderboards (signed-in players), a **Practice Room** that names any chord you play and can light up any scale or chord, with a metronome, and settings for sounds, key labels and MIDI.

**Accounts.** Anyone can play as a guest; progress is kept in the browser. Creating an account (email + password, Anvil Users service) saves progress on the server and brings the guest progress along.

## Level editor (`#admin`)

Sign in with an admin account. **Levels**: every territory's levels, reorder (▲▼), create (＋), edit name/territory/intro/thresholds/codex pages/composer cards/trial flag, and the steps, each with its own fields and a live preview (resolved chords for numerals, note counts and length for rushes, ▶ to hear it). Live checks match the server's. **Playtest** runs the unsaved level in the real engine. A level with errors is saved as a draft. Built-in levels can be put back with "↺ Original"; "Restore missing built-in levels" re-adds deleted ones. Raw JSON editing is available. **Territories**: name, emoji, blurb, colour, map position (with a live map preview), order, publish. **Players**: progress overview and admin rights.

**Admins.** `arkulinskis@gmail.com` becomes an admin the first time it signs in (`ADMIN_EMAILS` in `server_code/Game.py`). Tick `is_admin` in the users table, or use the Players tab, to add more.

## Project layout

```
native_libraries.html   fonts, colour tokens, window.DR helpers (bridge, modal, toast), the synthesized piano + sounds, input (MIDI/keys/mouse)
lib/music.js            music theory in the browser (same rules as server_code/Music.py), chord detection, staff positions
lib/art.js              the knowledge map, music staves, crests, composer medallions, the title scene
lib/engine.js           DR.Keyboard (on-screen piano) and DR.Stage (runs a level: every step type, scoring, rush highway)
forms/GamePage.html     the player app: title, sign-in, map, level card, play, results, codex, collection, practice room, badges, shop, settings
forms/AdminPage.html    admin sign-in + level editor + territories + players
forms/Main.html         the startup form (#admin → AdminPage, else GamePage)
client_code/*.py        thin Anvil forms; dr_ui.py is the JS⇄Python bridge, server-call whitelist and sign-in
server_code/Music.py    note names, chord symbols, Roman numerals, rush sequences
server_code/Catalog.py  codex pages, composer cards, shop items, badges, ranks, rewards
server_code/Levels.py   the level format, its checks, the daily practice generator, and the 42 built-in levels
server_code/Game.py     player callables + guest_* twins; all rules (scoring, unlocking, conquest, rewards, shop, daily)
server_code/Admin.py    the level editor's callables (admin only)
tools/                  sync/deploy to Anvil, tests, local dev server
```

Tables (all server-only): `users` (+ display_name, is_admin, progress, last_played), `territories`, `levels` (data is a Simple Object), `scores`. The built-in road is added to the tables the first time anyone loads the game.

The server checks every result: the item count must match the level, hits and stats are capped by what the level holds, and the accuracy must reach the level's pass mark.

## Working on it

```
python -I tools/check.py --ui                    # syntax, server tests, JS/Python parity, headless-Chrome tests → ALL CHECKS PASSED
python -I tools/preview/devserver.py 8765        # local game at http://localhost:8765/ (?as=ana, ?as=admin#admin)
python tools/deploy.py                           # dry run (needs PyYAML, so no -I)
python tools/deploy.py --push "Message"          # deploy: commit + push to GitHub, Anvil pulls it
```

## After the first deploy

1. Open the app in the Anvil editor. It shows a **Schema Mismatch** alert: choose **"The schema of the source code is correct"** so Anvil creates the tables.
2. Check the **Users** service is listed (the deploy adds it: email sign-in, sign-up allowed, no email confirmation).
3. Run the app and create an account with **arkulinskis@gmail.com** soon: email confirmation is off, so whoever first registers that email gets admin.
4. Optional: turn on email confirmation in the Users service, and pick a nicer app URL under Publish.
