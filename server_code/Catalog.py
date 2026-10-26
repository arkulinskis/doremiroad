# Catalog — Server Module (no callables). Everything a player can collect or buy, in one place.
# public() is what the browser gets; the game rules in Game.py read the same tables.

# ---------------------------------------------------------------- ranks (by XP)
RANKS = [
    (0, "Novice"), (200, "Busker"), (500, "Apprentice"), (1000, "Chorister"), (1800, "Accompanist"),
    (3000, "Soloist"), (5000, "Virtuoso"), (8000, "Maestro"), (12000, "Legend"),
]

# ---------------------------------------------------------------- the Codex: theory pages unlocked by levels
# ex: what "Hear it" plays. notes = one after another, chord = together, both = arpeggio then chord.
TOPICS = [
    {"key": "keyboard", "name": "The Keyboard"},
    {"key": "steps", "name": "Steps & Accidentals"},
    {"key": "scales", "name": "Scales"},
    {"key": "intervals", "name": "Intervals"},
    {"key": "chords", "name": "Chords"},
    {"key": "progressions", "name": "Progressions"},
    {"key": "reading", "name": "Reading Music"},
    {"key": "rhythm", "name": "Rhythm"},
    {"key": "blues", "name": "Blues & Jazz"},
    {"key": "keys", "name": "Keys"},
]

CODEX = [
    # The Keyboard
    {"key": "keyboard", "topic": "keyboard", "glyph": "\U0001F3B9", "title": "The Keyboard",
     "text": "Piano keys repeat a pattern of twelve: seven white keys and five black keys. The black keys come in "
             "groups of two and three. That pattern is your map: every note can be found from it.",
     "ex": {"notes": ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]}},
    {"key": "find_c", "topic": "keyboard", "glyph": "C", "title": "Finding C",
     "text": "C is the white key just to the left of each group of two black keys. The C nearest the middle of the "
             "piano is called middle C, written C4.",
     "ex": {"notes": ["C3", "C4", "C5"]}},
    {"key": "alphabet", "topic": "keyboard", "glyph": "A–G", "title": "The Musical Alphabet",
     "text": "White keys are named with seven letters, A to G, and then the letters start again. Counting up from C: "
             "C D E F G A B, then C again.",
     "ex": {"notes": ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]}},
    {"key": "octave", "topic": "keyboard", "glyph": "8va", "title": "Octaves",
     "text": "Two notes with the same letter, eight white keys apart, form an octave. The higher one vibrates exactly "
             "twice as fast, which is why they sound like the same note at a different height. Octaves are numbered: "
             "middle C is C4 and the next C up is C5.",
     "ex": {"notes": ["C4", "C5", "C4+C5"]}},
    # Steps & Accidentals
    {"key": "sharps_flats", "topic": "steps", "glyph": "♯♭", "title": "Sharps and Flats",
     "text": "A sharp (♯) raises a note to the very next key up; a flat (♭) lowers it to the next key down. The "
             "black key between C and D is both C♯ and D♭: two names for one sound, called enharmonic notes.",
     "ex": {"notes": ["C4", "C#4", "D4", "Db4"]}},
    {"key": "half_whole", "topic": "steps", "glyph": "½", "title": "Half and Whole Steps",
     "text": "A half step goes from one key to the very next key, black or white. A whole step is two half steps. "
             "E–F and B–C are half steps even though both are white keys: there is no black key between them.",
     "ex": {"notes": ["E4", "F4", "B4", "C5"]}},
    {"key": "chromatic", "topic": "steps", "glyph": "↑↑", "title": "The Chromatic Scale",
     "text": "Play every key in a row, black and white, and you move in half steps: the chromatic scale. Twelve half "
             "steps take you up exactly one octave.",
     "ex": {"notes": ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4", "C5"]}},
    # Scales
    {"key": "major_scale", "topic": "scales", "glyph": "↑", "title": "The Major Scale",
     "text": "A major scale follows the pattern whole, whole, half, whole, whole, whole, half. Starting on C it uses "
             "only white keys: C D E F G A B C. The same pattern started on any key gives that key's major scale.",
     "ex": {"notes": ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]}},
    {"key": "g_major", "topic": "scales", "glyph": "G", "title": "G Major",
     "text": "Start the major pattern on G and the seventh note has to be F♯ to keep the half step just below the "
             "top. G major has one sharp: F♯.",
     "ex": {"notes": ["G4", "A4", "B4", "C5", "D5", "E5", "F#5", "G5"]}},
    {"key": "f_major", "topic": "scales", "glyph": "F", "title": "F Major",
     "text": "Start the major pattern on F and the fourth note has to be B♭, a half step above A. F major has one "
             "flat: B♭.",
     "ex": {"notes": ["F4", "G4", "A4", "Bb4", "C5", "D5", "E5", "F5"]}},
    {"key": "pentatonic", "topic": "scales", "glyph": "5", "title": "The Pentatonic Scale",
     "text": "Five notes instead of seven: the major scale without its 4th and 7th, so C D E G A. With no half steps it "
             "is hard to hit a note that clashes, which is why it carries melodies all over the world, from folk songs "
             "to rock solos. The five black keys form a pentatonic scale too.",
     "ex": {"notes": ["C4", "D4", "E4", "G4", "A4", "C5"]}},
    {"key": "natural_minor", "topic": "scales", "glyph": "↓", "title": "The Natural Minor Scale",
     "text": "The natural minor scale follows whole, half, whole, whole, half, whole, whole. A minor uses only white "
             "keys: A B C D E F G A. Its lowered 3rd gives it a darker, more serious colour.",
     "ex": {"notes": ["A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4"]}},
    {"key": "relative", "topic": "scales", "glyph": "⇄", "title": "Relative Keys",
     "text": "Every major key shares its notes with a minor key that starts three half steps lower. C major and A minor "
             "are relatives; so are G major and E minor, and F major and D minor.",
     "ex": {"notes": ["C4+E4+G4", "A3+C4+E4"]}},
    {"key": "harmonic_minor", "topic": "scales", "glyph": "♯7", "title": "Harmonic Minor",
     "text": "Raise the 7th note of the natural minor by a half step and you get the harmonic minor: A B C D E F G♯ A. "
             "The raised 7th pulls hard towards the home note and gives the scale its dramatic sound.",
     "ex": {"notes": ["A3", "B3", "C4", "D4", "E4", "F4", "G#4", "A4"]}},
    {"key": "modes", "topic": "scales", "glyph": "◐", "title": "Modes",
     "text": "Play the white keys from D to D and you get the Dorian mode; from G to G, the Mixolydian. Same notes as "
             "C major, new home note, new mood: Dorian is minor with a bright 6th, Mixolydian is major with a flat 7th.",
     "ex": {"notes": ["D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5"]}},
    # Intervals
    {"key": "intervals", "topic": "intervals", "glyph": "↔", "title": "Intervals",
     "text": "An interval is the distance between two notes, counted in letter names including both ends. C to E is a "
             "3rd (C, D, E); C to G is a 5th (C, D, E, F, G).",
     "ex": {"notes": ["C4", "E4", "C4", "G4"]}},
    {"key": "thirds", "topic": "intervals", "glyph": "3", "title": "Major and Minor Thirds",
     "text": "A major 3rd spans four half steps (C–E); a minor 3rd spans three (C–E♭). Thirds are the bricks "
             "chords are built from, and the difference between them is the difference between major and minor.",
     "ex": {"notes": ["C4+E4", "C4+Eb4"]}},
    {"key": "fifths", "topic": "intervals", "glyph": "5th", "title": "The Perfect Fifth",
     "text": "Seven half steps, C to G. After the octave, the perfect 5th is the most stable interval there is, and it is "
             "the backbone of nearly every chord.",
     "ex": {"notes": ["C4", "G4", "C4+G4"]}},
    {"key": "dominant", "topic": "intervals", "glyph": "V", "title": "The Dominant",
     "text": "The 5th note of a key, and the chord built on it. The dominant chord contains the leading tone, a half "
             "step below home (B in C major), which is why V pulls so strongly back to I.",
     "ex": {"notes": ["G3+B3+D4", "C4+E4+G4"]}},
    # Chords
    {"key": "triads", "topic": "chords", "glyph": "∴", "title": "Triads",
     "text": "A triad is three notes stacked in thirds: a root, a 3rd and a 5th. On the white keys, skip one key between "
             "each note: C–E–G, D–F–A, E–G–B and so on.",
     "ex": {"notes": ["C4", "E4", "G4", "C4+E4+G4"]}},
    {"key": "major_chord", "topic": "chords", "glyph": "M", "title": "Major Chords",
     "text": "Root, then a major 3rd (four half steps), then a minor 3rd on top (three more). C major is C–E–G. "
             "Major chords sound bright and settled.",
     "ex": {"notes": ["C4+E4+G4", "F4+A4+C5", "G3+B3+D4"]}},
    {"key": "minor_chord", "topic": "chords", "glyph": "m", "title": "Minor Chords",
     "text": "Root, then a minor 3rd (three half steps), then a major 3rd (four more). A minor is A–C–E. Lower the "
             "middle note of any major chord by a half step and it turns minor.",
     "ex": {"notes": ["C4+E4+G4", "C4+Eb4+G4", "A3+C4+E4"]}},
    {"key": "dim_aug", "topic": "chords", "glyph": "°+", "title": "Diminished and Augmented",
     "text": "Stack two minor 3rds and you get a diminished chord (B–D–F): tense and unstable. Stack two major "
             "3rds and you get an augmented chord (C–E–G♯): floating and unresolved.",
     "ex": {"notes": ["B3+D4+F4", "C4+E4+G#4"]}},
    {"key": "inversions", "topic": "chords", "glyph": "↻", "title": "Inversions",
     "text": "A chord keeps its name when its notes are reordered. C–E–G is root position, E–G–C the first "
             "inversion and G–C–E the second. Inversions let your hand move less between chords.",
     "ex": {"notes": ["C4+E4+G4", "E4+G4+C5", "G4+C5+E5"]}},
    {"key": "sevenths", "topic": "chords", "glyph": "7", "title": "Seventh Chords",
     "text": "Add one more 3rd on top of a triad and you get a seventh chord. Cmaj7 (C–E–G–B) is dreamy, C7 "
             "(C–E–G–B♭) wants to move on, Cm7 (C–E♭–G–B♭) is smooth and mellow.",
     "ex": {"notes": ["C4+E4+G4+B4", "C4+E4+G4+Bb4", "C4+Eb4+G4+Bb4"]}},
    # Progressions
    {"key": "numerals", "topic": "progressions", "glyph": "IV", "title": "Roman Numerals",
     "text": "Chords in a key are numbered by the scale note they start on. Upper case means major, lower case minor, "
             "° diminished. In C major: I = C, ii = Dm, iii = Em, IV = F, V = G, vi = Am, vii° = B°.",
     "ex": {"notes": ["C4+E4+G4", "D4+F4+A4", "E4+G4+B4", "F4+A4+C5", "G4+B4+D5", "A4+C5+E5"]}},
    {"key": "one_four_five", "topic": "progressions", "glyph": "I–IV–V", "title": "I – IV – V",
     "text": "The three major chords of a key. Between them they contain every note of the scale, and they carry "
             "countless folk, rock and blues songs. In C: C, F and G.",
     "ex": {"notes": ["C4+E4+G4", "F4+A4+C5", "G3+B3+D4", "C4+E4+G4"]}},
    {"key": "cadences", "topic": "progressions", "glyph": "‖", "title": "Cadences",
     "text": "A cadence is how a phrase ends. V to I is the authentic cadence, the strongest full stop in music. IV to I "
             "is the plagal or 'Amen' cadence. Stopping on V is a half cadence, more like a comma.",
     "ex": {"notes": ["G3+B3+D4", "C4+E4+G4", "F4+A4+C5", "C4+E4+G4"]}},
    {"key": "pop_progression", "topic": "progressions", "glyph": "I–V–vi–IV", "title": "I – V – vi – IV",
     "text": "Perhaps the most used progression in modern pop: C – G – Am – F. Start the same loop on vi "
             "(Am – F – C – G) and the same four chords sound more wistful.",
     "ex": {"notes": ["C4+E4+G4", "G3+B3+D4", "A3+C4+E4", "F3+A3+C4"]}},
    {"key": "fifties", "topic": "progressions", "glyph": "I–vi–IV–V", "title": "I – vi – IV – V",
     "text": "The 1950s 'doo-wop' progression: C – Am – F – G. It has carried ballads and pop songs for decades.",
     "ex": {"notes": ["C4+E4+G4", "A3+C4+E4", "F3+A3+C4", "G3+B3+D4"]}},
    {"key": "canon", "topic": "progressions", "glyph": "∞", "title": "The Canon Progression",
     "text": "Pachelbel's Canon walks downhill: I – V – vi – iii – IV – I – IV – V (in C: C G Am Em F C F G). "
             "Many songs borrow it, knowingly or not.",
     "ex": {"notes": ["C4+E4+G4", "G3+B3+D4", "A3+C4+E4", "E3+G3+B3", "F3+A3+C4", "C4+E4+G4", "F3+A3+C4", "G3+B3+D4"]}},
    # Reading Music
    {"key": "staff", "topic": "reading", "glyph": "≡", "title": "The Staff",
     "text": "Music is written on five lines called the staff. Notes sit on the lines or in the spaces between them; the "
             "higher on the staff, the higher the note. Each step from a line to the next space is the next letter.",
     "ex": {"notes": ["E4", "F4", "G4", "A4", "B4"]}},
    {"key": "treble", "topic": "reading", "glyph": "\U0001D11E", "title": "Treble Clef",
     "text": "The treble clef curls around the second line, marking it as G above middle C. That is why it is also "
             "called the G clef. Lines from the bottom: E G B D F. Spaces: F A C E.",
     "ex": {"notes": ["E4", "G4", "B4", "D5", "F5"]}},
    {"key": "bass", "topic": "reading", "glyph": "\U0001D122", "title": "Bass Clef",
     "text": "The bass clef's two dots sit either side of the fourth line, marking it as F below middle C, so it is also "
             "called the F clef. Lines from the bottom: G B D F A. Spaces: A C E G.",
     "ex": {"notes": ["G2", "B2", "D3", "F3", "A3"]}},
    {"key": "ledger", "topic": "reading", "glyph": "—", "title": "Ledger Lines and Middle C",
     "text": "Short extra lines, called ledger lines, extend the staff up or down. Middle C sits on one ledger line below "
             "the treble staff and one ledger line above the bass staff: the same note joins the two.",
     "ex": {"notes": ["A3", "B3", "C4", "D4", "E4"]}},
    # Rhythm
    {"key": "rhythm", "topic": "rhythm", "glyph": "♩", "title": "Beats and Note Values",
     "text": "Music moves on a steady beat. A quarter note lasts one beat, a half note two, a whole note four and an "
             "eighth note half a beat. The tempo, in beats per minute (BPM), sets how fast the beat goes.",
     "ex": {"notes": ["C4", "C4", "C4", "C4"]}},
    {"key": "time_sig", "topic": "rhythm", "glyph": "¾", "title": "Time Signatures",
     "text": "4/4 means four beats in every bar; 3/4 has three, the lilt of a waltz or a minuet. Bar lines group the "
             "beats, so you can feel where the strong first beat of each bar lands.",
     "ex": {"notes": ["G3+B3+D4", "D4", "D4"]}},
    # Blues & Jazz
    {"key": "blues_scale", "topic": "blues", "glyph": "♭5", "title": "The Blues Scale",
     "text": "The minor pentatonic plus one extra 'blue note': C E♭ F G♭ G B♭ C. That G♭, the flattened "
             "5th, is what makes it sound like the blues.",
     "ex": {"notes": ["C4", "Eb4", "F4", "Gb4", "G4", "Bb4", "C5"]}},
    {"key": "twelve_bar", "topic": "blues", "glyph": "12", "title": "The Twelve-Bar Blues",
     "text": "Twelve bars of I, IV and V, usually played as dominant 7ths: I I I I | IV IV I I | V IV I V. It is the "
             "foundation of the blues, early rock 'n' roll and a great deal of jazz.",
     "ex": {"notes": ["C4+E4+G4+Bb4", "F3+A3+C4+Eb4", "C4+E4+G4+Bb4", "G3+B3+D4+F4"]}},
    {"key": "two_five_one", "topic": "blues", "glyph": "ii–V–I", "title": "ii – V – I",
     "text": "The core move of jazz harmony: Dm7 – G7 – Cmaj7. Each root falls a fifth to the next, which makes the "
             "arrival on I feel inevitable.",
     "ex": {"notes": ["D4+F4+A4+C5", "G3+B3+D4+F4", "C4+E4+G4+B4"]}},
    # Keys
    {"key": "circle", "topic": "keys", "glyph": "○", "title": "The Circle of Fifths",
     "text": "Go up a fifth from C and you reach G (one sharp), then D (two sharps), then A (three). Go down a fifth from C "
             "and you reach F (one flat), then B♭ (two flats). The circle shows every key and how closely related they are.",
     "ex": {"notes": ["C4", "G4", "D4", "A4", "E4", "B4"]}},
    {"key": "key_sigs", "topic": "keys", "glyph": "♯♯", "title": "Key Signatures",
     "text": "The sharps or flats at the start of each staff tell you the key. Sharps are always added in the order "
             "F C G D A E B, flats in the reverse order: B E A D G C F.",
     "ex": {"notes": ["D4", "E4", "F#4", "G4", "A4", "B4", "C#5", "D5"]}},
]
CODEX_BY_KEY = {c["key"]: c for c in CODEX}

# ---------------------------------------------------------------- composer cards
RARITY = {
    "common": {"name": "Common", "order": 0, "dupe": 20},
    "rare": {"name": "Rare", "order": 1, "dupe": 40},
    "epic": {"name": "Epic", "order": 2, "dupe": 80},
    "legendary": {"name": "Legendary", "order": 3, "dupe": 150},
}
COMPOSERS = [
    {"key": "vivaldi", "name": "Antonio Vivaldi", "years": "1678–1741", "era": "Baroque", "rarity": "common",
     "fact": "A violinist and priest from Venice who wrote hundreds of concertos. The Four Seasons is his best-known set."},
    {"key": "handel", "name": "George Frideric Handel", "years": "1685–1759", "era": "Baroque", "rarity": "common",
     "fact": "German-born, he made his career in London. He wrote Messiah, with its Hallelujah chorus, in about three weeks."},
    {"key": "haydn", "name": "Joseph Haydn", "years": "1732–1809", "era": "Classical", "rarity": "common",
     "fact": "Known as the 'Father of the Symphony': he wrote over a hundred of them, and was a friend and mentor to Mozart."},
    {"key": "schubert", "name": "Franz Schubert", "years": "1797–1828", "era": "Romantic", "rarity": "common",
     "fact": "Wrote more than 600 songs and some of the finest piano music ever, all before he died at just 31."},
    {"key": "satie", "name": "Erik Satie", "years": "1866–1925", "era": "Modern", "rarity": "common",
     "fact": "An eccentric Parisian whose calm, sparse Gymnopédies (1888) still sound modern today."},
    {"key": "grieg", "name": "Edvard Grieg", "years": "1843–1907", "era": "Romantic", "rarity": "common",
     "fact": "Norway's best-loved composer. He wrote 'In the Hall of the Mountain King' for the play Peer Gynt."},
    {"key": "mendelssohn", "name": "Felix Mendelssohn", "years": "1809–1847", "era": "Romantic", "rarity": "common",
     "fact": "A child prodigy who later conducted Bach's St Matthew Passion in 1829 and brought Bach's music back into fashion."},
    {"key": "fanny", "name": "Fanny Mendelssohn", "years": "1805–1847", "era": "Romantic", "rarity": "common",
     "fact": "Felix's sister and a brilliant pianist who wrote over 450 pieces; a few were first published under her brother's name."},
    {"key": "chopin", "name": "Frédéric Chopin", "years": "1810–1849", "era": "Romantic", "rarity": "rare",
     "fact": "The 'poet of the piano': almost everything he wrote is for solo piano, from nocturnes and études to waltzes."},
    {"key": "liszt", "name": "Franz Liszt", "years": "1811–1886", "era": "Romantic", "rarity": "rare",
     "fact": "Perhaps the greatest pianist of his age. He made the solo piano recital a thing; his fans' frenzy was called 'Lisztomania'."},
    {"key": "clara", "name": "Clara Schumann", "years": "1819–1896", "era": "Romantic", "rarity": "rare",
     "fact": "A star pianist from her teens who performed for more than sixty years. She began her Piano Concerto at 13."},
    {"key": "tchaikovsky", "name": "Pyotr Ilyich Tchaikovsky", "years": "1840–1893", "era": "Romantic", "rarity": "rare",
     "fact": "Wrote the ballets Swan Lake, The Sleeping Beauty and The Nutcracker."},
    {"key": "joplin", "name": "Scott Joplin", "years": "c.1868–1917", "era": "Ragtime", "rarity": "rare",
     "fact": "The 'King of Ragtime'. Maple Leaf Rag made his name; The Entertainer became famous again in the 1970s."},
    {"key": "rachmaninoff", "name": "Sergei Rachmaninoff", "years": "1873–1943", "era": "Late Romantic", "rarity": "rare",
     "fact": "A virtuoso with famously large hands. His piano concertos are among the most demanding, and most loved, ever written."},
    {"key": "mozart", "name": "Wolfgang Amadeus Mozart", "years": "1756–1791", "era": "Classical", "rarity": "epic",
     "fact": "Composing from the age of five, he wrote over 600 works, including operas, symphonies and 27 piano concertos, in 35 years."},
    {"key": "debussy", "name": "Claude Debussy", "years": "1862–1918", "era": "Impressionist", "rarity": "epic",
     "fact": "Bent the old rules with whole-tone scales and floating chords. Clair de lune is his."},
    {"key": "gershwin", "name": "George Gershwin", "years": "1898–1937", "era": "Jazz Age", "rarity": "epic",
     "fact": "Blended jazz and the concert hall in Rhapsody in Blue (1924), and wrote the opera Porgy and Bess."},
    {"key": "ellington", "name": "Duke Ellington", "years": "1899–1974", "era": "Jazz", "rarity": "epic",
     "fact": "Pianist and bandleader for half a century, with well over a thousand compositions to his name."},
    {"key": "bach", "name": "Johann Sebastian Bach", "years": "1685–1750", "era": "Baroque", "rarity": "legendary",
     "fact": "His Well-Tempered Clavier has a prelude and fugue in every one of the 24 major and minor keys."},
    {"key": "beethoven", "name": "Ludwig van Beethoven", "years": "1770–1827", "era": "Classical / Romantic", "rarity": "legendary",
     "fact": "Kept composing as he lost his hearing. His Ninth Symphony (1824) ends with the Ode to Joy you played on Ivory Shore."},
]
COMPOSER_BY_KEY = {c["key"]: c for c in COMPOSERS}

# ---------------------------------------------------------------- the shop (paid in ducats)
SKINS = [  # the on-screen keyboard
    {"key": "ivory", "name": "Concert Ivory", "price": 0, "desc": "Classic black and white."},
    {"key": "rosewood", "name": "Rosewood Upright", "price": 150, "desc": "Warm wood cheeks and aged ivory."},
    {"key": "ebony", "name": "Ebony Grand", "price": 200, "desc": "Inverted: dark naturals, pearl sharps."},
    {"key": "jade", "name": "Jade Court", "price": 250, "desc": "Pale jade keys with gold seams."},
    {"key": "neon", "name": "Neon Synth", "price": 300, "desc": "A glowing 80s synthesizer."},
    {"key": "glass", "name": "Glass Harmonica", "price": 400, "desc": "Frosted glass that catches the light."},
    {"key": "gilded", "name": "Gilded Hall", "price": 500, "desc": "Gold leaf for a concert hall."},
]
TRAILS = [  # the falling notes in rush challenges
    {"key": "lantern", "name": "Lantern", "price": 0, "desc": "Warm gold lights."},
    {"key": "ember", "name": "Ember", "price": 120, "desc": "Notes that burn on the way down."},
    {"key": "frost", "name": "Frost", "price": 150, "desc": "Cold blue crystal."},
    {"key": "aurora", "name": "Aurora", "price": 200, "desc": "Green and violet northern lights."},
    {"key": "prism", "name": "Prism", "price": 350, "desc": "Every pitch its own colour."},
]
BANNERS = [  # your colour on the knowledge map
    {"key": "crimson", "name": "Crimson", "color": "#c8434e", "price": 0},
    {"key": "azure", "name": "Azure", "color": "#3f86d6", "price": 80},
    {"key": "emerald", "name": "Emerald", "color": "#2f9e6e", "price": 80},
    {"key": "violet", "name": "Violet", "color": "#8a5cc9", "price": 80},
    {"key": "amber", "name": "Amber", "color": "#e09a2d", "price": 80},
    {"key": "onyx", "name": "Onyx", "color": "#2b2d36", "price": 150},
    {"key": "pearl", "name": "Pearl", "color": "#e9e2d0", "price": 150},
]
SHOP = {"skins": SKINS, "trails": TRAILS, "banners": BANNERS}
SHOP_BY_KEY = {kind: {x["key"]: x for x in items} for kind, items in SHOP.items()}
DEFAULTS = {"skins": "ivory", "trails": "lantern", "banners": "crimson"}

# ---------------------------------------------------------------- rewards
REWARDS = {
    "xp_first": 50, "xp_per_item": 5, "xp_star": 25, "xp_replay": 10, "xp_daily": 40,
    "ducats_first": 40, "ducats_star": 15, "ducats_replay": 5, "ducats_replay_star": 2,
    "daily_ducats": 30, "daily_streak_bonus": 10, "daily_streak_cap": 7, "daily_card_chance": 0.35,
}

# ---------------------------------------------------------------- badges
# "stat"+"at": unlocked when progress.stats[stat] >= at. Otherwise Game.check_badges has the test.
BADGES = [
    {"key": "first_note", "name": "First Note", "emoji": "\U0001F3B5", "desc": "Clear your first level."},
    {"key": "road_10", "name": "Ten Milestones", "emoji": "\U0001FAA7", "desc": "Clear 10 levels."},
    {"key": "road_25", "name": "The Long Road", "emoji": "\U0001F6E4️", "desc": "Clear 25 levels."},
    {"key": "road_all", "name": "Journey's End", "emoji": "\U0001F3C1", "desc": "Clear every level on the road."},
    {"key": "stars_30", "name": "Starlit", "emoji": "✨", "desc": "Earn 30 stars."},
    {"key": "stars_75", "name": "Constellation", "emoji": "\U0001F30C", "desc": "Earn 75 stars."},
    {"key": "first_flag", "name": "First Banner", "emoji": "\U0001F6A9", "desc": "Conquer a territory."},
    {"key": "flags_5", "name": "Five Banners", "emoji": "\U0001F3F0", "desc": "Conquer 5 territories."},
    {"key": "flags_all", "name": "Realm United", "emoji": "\U0001F451", "desc": "Conquer the whole knowledge map."},
    {"key": "mastery", "name": "Master of a Realm", "emoji": "\U0001F3C6", "desc": "Three-star every level in a territory."},
    {"key": "flawless", "name": "Flawless", "emoji": "\U0001F48E", "desc": "Finish a level with 100% accuracy.", "stat": "flawless", "at": 1},
    {"key": "flawless_10", "name": "Immaculate", "emoji": "\U0001F4A0", "desc": "Finish 10 levels with 100% accuracy.", "stat": "flawless", "at": 10},
    {"key": "combo_25", "name": "In the Groove", "emoji": "\U0001F525", "desc": "Hit a 25-note combo in a rush.", "stat": "max_combo", "at": 25},
    {"key": "combo_60", "name": "Unstoppable", "emoji": "⚡", "desc": "Hit a 60-note combo in a rush.", "stat": "max_combo", "at": 60},
    {"key": "perfect_200", "name": "Pinpoint", "emoji": "\U0001F3AF", "desc": "Land 200 perfect hits in rushes.", "stat": "perfects", "at": 200},
    {"key": "notes_500", "name": "Busy Fingers", "emoji": "\U0001F590️", "desc": "Play 500 correct notes.", "stat": "notes", "at": 500},
    {"key": "notes_3000", "name": "Iron Fingers", "emoji": "\U0001F9BE", "desc": "Play 3,000 correct notes.", "stat": "notes", "at": 3000},
    {"key": "chords_100", "name": "Chord Smith", "emoji": "\U0001F528", "desc": "Play 100 correct chords.", "stat": "chords", "at": 100},
    {"key": "chords_500", "name": "Harmonist", "emoji": "\U0001F3BC", "desc": "Play 500 correct chords.", "stat": "chords", "at": 500},
    {"key": "ear_25", "name": "Keen Ear", "emoji": "\U0001F442", "desc": "Answer 25 ear-training questions right.", "stat": "ear", "at": 25},
    {"key": "ear_100", "name": "Golden Ear", "emoji": "\U0001F9BB", "desc": "Answer 100 ear-training questions right.", "stat": "ear", "at": 100},
    {"key": "quiz_25", "name": "Theorist", "emoji": "\U0001F4D0", "desc": "Answer 25 theory questions right.", "stat": "quiz", "at": 25},
    {"key": "codex_10", "name": "Scholar", "emoji": "\U0001F4D6", "desc": "Unlock 10 Codex pages."},
    {"key": "codex_all", "name": "Encyclopedist", "emoji": "\U0001F4DA", "desc": "Unlock every Codex page."},
    {"key": "cards_5", "name": "Patron of the Arts", "emoji": "\U0001F0CF", "desc": "Collect 5 composer cards."},
    {"key": "cards_all", "name": "Hall of Fame", "emoji": "\U0001F3DB️", "desc": "Collect every composer card."},
    {"key": "daily_3", "name": "Good Habit", "emoji": "\U0001F4C5", "desc": "Practise 3 days in a row."},
    {"key": "daily_7", "name": "Devoted", "emoji": "\U0001F5D3️", "desc": "Practise 7 days in a row."},
    {"key": "daily_30", "name": "Disciplined", "emoji": "\U0001F9ED", "desc": "Practise 30 days in a row."},
    {"key": "midi", "name": "Plugged In", "emoji": "\U0001F50C", "desc": "Finish a level on a MIDI keyboard.", "stat": "midi_runs", "at": 1},
    {"key": "stylist", "name": "Stylist", "emoji": "\U0001F3A8", "desc": "Buy something in the shop."},
    {"key": "virtuoso", "name": "Virtuoso", "emoji": "\U0001F3BB", "desc": "Reach the rank of Virtuoso."},
]
BADGE_KEYS = {b["key"] for b in BADGES}

# Territory colours the admin can pick from (the map is drawn from these).
COLORS = ["#d1b98a", "#4f8c66", "#8b93b8", "#c47a55", "#5e9690", "#cfa245", "#9a6fae", "#4c7cc4", "#d05e6a",
          "#7f9c4a", "#b06a8f", "#6a8fa0"]


def public():
    """The catalog the browser gets."""
    return {"ranks": [{"xp": x, "name": n} for x, n in RANKS], "topics": TOPICS, "codex": CODEX,
            "rarity": RARITY, "composers": COMPOSERS, "shop": SHOP, "defaults": DEFAULTS, "badges": BADGES,
            "rewards": REWARDS, "colors": COLORS}
