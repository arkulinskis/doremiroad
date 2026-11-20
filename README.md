# Doremi Road

A piano-learning game for [anvil.works](https://anvil.works). You travel a road across the **Realm of Harmony**, a map of musical knowledge. Each territory teaches one part of music; every level you clear claims one of its provinces in your banner colour, and clearing them all conquers the territory and opens the next.

- **App repo:** github.com/arkulinskis/doremiroad (branch `master`). Anvil pulls `master`.
- **Level editor:** open the app with `#admin` at the end of the URL.

## Playing

Play with a **MIDI keyboard** (Web MIDI: Chrome or Edge), the **computer keyboard** (`Z`–`M` and `Q`–`U` are two octaves, black keys on the row above, `↑`/`↓` shift octave), the **mouse**, or the **touch-screen piano** on a tablet or phone. By default any octave counts; steps marked "exact" need the right octave.

**Touch-screen piano.** On tablets and phones (any screen whose main pointer is a finger) the on-screen keys switch to touch mode: taller keys, no computer-key letters, "Tap the keys" hints, several fingers at once for chords, slide along the keys for a glissando, and tapping lower on a key plays louder. The Practice Room fits as many octaves as a finger can use (white keys at least ~46px) and has ◀ ▶ octave buttons (remembered; also on desktop). Settings → **Touch-screen piano**: Auto / On / Off. iPhone/iPad sound plays even with the silent switch on (Safari 17+); notes stop when the app goes to the background. A phone held sideways gets a compact level screen.

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
5. **34 badges** (Caroler and Songbook come from the Song Shelf).
6. **Stars** (3 per level) and **ranks** by XP: Novice → Busker → Apprentice → Chorister → Accompanist → Soloist → Virtuoso → Maestro → Legend.
7. **Shop** (paid in ducats): 7 keyboard skins, 5 note trails for rushes, 7 map banners.
8. **Daily Practice**: a new generated level every day (harder as you conquer more), streak bonus, card chance.

## Song Shelf (`#songs`)

17 public-domain songs on two shelves, open to everyone from the first minute (guests too): **Christmas** (Jingle Bells, We Wish You a Merry Christmas, Deck the Halls, O Christmas Tree, Silent Night, Joy to the World) and **Favourites** (Twinkle, Mary Had a Little Lamb, London Bridge, Ode to Joy, Row Your Boat, Happy Birthday, When the Saints, Amazing Grace, Can-Can, Für Elise, Minuet in G). Every song plays three ways, each with its own stars: **🐢 Learn** (phrase by phrase, the glowing key waits for you), **🎯 Practice** (falling notes at 70% speed, with names) and **⭐ Perform** (full tempo). "♪ Hear it" plays the opening. The first clear of each mode pays XP and ducats. The title screen has "🎄 Play Jingle Bells now" from 15 Nov to 10 Jan ("🎵 Play a song now" the rest of the year). Melodies live in `server_code/Songs.py`, written out by hand, melody only.

## Too fast? Too laggy?

- **Slow it down:** the level card of any level with a rush has a 100% / 75% / 50% speed choice, and a failed rush offers "🐢 Try at 75% speed" (then 50%). A slowed run clears the level and opens the next one, with one star at most and no leaderboard score. On the Song Shelf, a failed Perform offers Practice and a failed Practice offers Learn.
- **Timing:** Settings → Timing (−/+ 10 ms, 0 to 300 ms) and **Calibrate**: tap with the beat as dots land on a line; the median lateness is taken off every rush press (Bluetooth speakers and TVs lag).

## Homework links and the weekly report (no accounts)

- **Teachers** (`#teacher`): pick up to 6 tasks (a song and how to play it, a road level, Daily Practice), a weekly goal ("15 minutes on 5 days"), a due date and a note, and get a link to copy or share.
- **Students** open `#hw/<code>`: "Homework from Ms Lee", a checklist that ticks itself from real play (the practice log), Play buttons, and a Homework tab with a dot in the header until it's all done. Kept only in that browser.
- **My practice week** (`#report`): minutes per day for the last 7 days (CSS bars), runs, levels and songs cleared, streak, stars, territory and the homework ticks. **Send to my teacher** shares it as a link (`#r/<code>`, read-only for the teacher); **Print** gives one page with a line for a parent's initials.
- Nothing about students is stored on the server: homework and reports travel inside their links (base64url JSON). The player's progress keeps a practice log (`progress.log`: seconds, runs and what was cleared per day, newest 60 days) that finished runs, failed or quit runs and Practice Room sessions over 30 s add to.

Also: per-level leaderboards (signed-in players), a **Practice Room** that names any chord you play and can light up any scale or chord, with a metronome, and settings for sounds, key labels and MIDI.

**Accounts.** Anyone can play as a guest; progress is kept in the browser. Creating an account (email + password, Anvil Users service) saves progress on the server and brings the guest progress along.

## Level editor (`#admin`)

Sign in with an admin account. **Levels**: every territory's levels, reorder (▲▼), create (＋), edit name/territory/intro/thresholds/codex pages/composer cards/trial flag, and the steps, each with its own fields and a live preview (resolved chords for numerals, note counts and length for rushes, ▶ to hear it). Live checks match the server's. **Playtest** runs the unsaved level in the real engine. A level with errors is saved as a draft. Built-in levels can be put back with "↺ Original"; "Restore missing built-in levels" re-adds deleted ones. Raw JSON editing is available. **Territories**: name, emoji, blurb, colour, map position (with a live map preview), order, publish. **Players**: progress overview and admin rights.

**Admins.** your admin email (App Secret `admin_emails`) becomes an admin the first time it signs in (`ADMIN_EMAILS` in `server_code/Game.py`). Tick `is_admin` in the users table, or use the Players tab, to add more.

## Project layout (native Anvil Forms since 2026-11-08, branch `forms`)

```
anvil.yaml              startup module, db_schema (unchanged), services, head_html (SEO, fonts, Prepsto, theme assets)
client_code/            startup.py, router.py (addresses: "" / #landing, #map, #songs, #codex, #collection, #practice,
                        #badges, #shop, #play/<level>[/75|50] | daily | song/<key>/<mode>, #teacher, #hw/<code>,
                        #report, #r/<code>, #auth, #admin), state.py, auth.py, legal.py (kit), game.py (the player's
                        state + lookups), dr.py (the bridge to the JavaScript engines), homework.py (homework + report codes)
  Layouts/Shell         the hub bar (tabs, rank, ducats, streak, profile button) + footer
  Pages/                Landing (title + Watch + How to play), Map, Songs, Codex, Collection, Practice, Badges, Shop,
                        Play, Teacher, Homework, Report, Auth, Admin (level editor: Levels / Territories / Players)
  Components/           Stage (the level engine), KnowledgeMap, TitleScene, Keys (on-screen piano), Art (SVG), SettingsPanel
  Items/                RepeatingPanel rows (levels, codex tiles, cards, badges, shop items, editor steps ...)
  Dialogs/              LevelCard, DailyCard, Pause, Fail, Results, CodexPage, ComposerView, Settings, Profile, LevelJson,
                        Calibrate
theme/assets/           dr-core.js (sound + MIDI/keys/touch input), dr-music.js, dr-art.js, dr-engine.js (unchanged
                        engines), dr-ui.js (practice room, shop previews, editor checks), ark-music.js, app.css, app-kit.js
server_code/            Music, Catalog, Levels, Songs (the Song Shelf), Game, Admin, Accounts (get_me), legal_server, seo_routes,
                        SchemaCheck
tools/                  check.py, ui_test.py + ui/smoke.js, testing/ (server tests), assets.py, icons
```

Tables (all server-only): `users` (+ display_name, is_admin, progress, last_played), `territories`, `levels` (data is a Simple Object), `scores`. The built-in road is added to the tables the first time anyone loads the game.

The server checks every result: the item count must match the level, hits and stats are capped by what the level holds, and the accuracy must reach the level's pass mark.

<!-- libraries:start -->
## Libraries and outside services

What this project uses besides its own code. Generated by `APP_MAKER/tools/libraries.py`; to change it, edit `APP_MAKER/libraries/catalog.py` and re-run the script.

| Name | How it gets in | Used here for |
|---|---|---|
| [Arkvital music library (ArkMusic)](https://arkvital-media.addanapp.workers.dev) | Outside web service | Background music: the user's licensed Audiio tracks, streamed from our own Cloudflare R2 bucket by a small shared player. |
| [YouTube embeds](https://developers.google.com/youtube/player_parameters) | Outside web service | Plays a YouTube video inside the page (the privacy-friendlier youtube-nocookie address). |
| [Google Fonts](https://fonts.google.com) | Loaded from a CDN | Cinzel, Cormorant Garamond, Inter, Noto Music |

**Built into the browser:** Canvas 2D, Web Audio API, Web Share, localStorage, Clipboard.

**Anvil platform:** Anvil, Anvil Data Tables, Anvil Email, Anvil JS bridge (anvil.js), Anvil Secrets, Anvil Users, Anvil Google service.

**Build and test tools (not shipped):** axe-core, Node.js, Headless Chrome (DevTools Protocol), PyYAML.

<!-- libraries:end -->

## Working on it

```
python tools/check.py                            # Anvil validator, JS syntax, asset hashes, server tests -> ALL CHECKS PASSED
python -I tools/ui_test.py --only smoke.js       # every page in the local Anvil App Server (Docker) -> ALL UI TESTS PASSED
git push origin forms                            # the branch; master only after the user's test
```

## After the first deploy

1. Open the app in the Anvil editor. It shows a **Schema Mismatch** alert: choose **"The schema of the source code is correct"** so Anvil creates the tables.
2. Check the **Users** service is listed (the deploy adds it: email sign-in, sign-up allowed, no email confirmation).
3. Run the app and create an account with **your admin email** (App Secret `admin_emails`) soon: email confirmation is off, so whoever first registers that email gets admin.
4. Optional: turn on email confirmation in the Users service, and pick a nicer app URL under Publish.
