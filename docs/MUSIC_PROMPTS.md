# Music Prompts — ElevenLabs Music

Drop-in prompts for [ElevenLabs Music](https://elevenlabs.io/music). Each entry has:
- **Use** — where the track plays
- **Duration** — how long to generate (seconds)
- **Loops** — yes/no (set the loopable flag in the API or trim the tail before importing)
- **Prompt** — paste this directly into the prompt field

Place rendered MP3/OGG files at `static/assets/audio/music/<id>.ogg`. (Audio is not yet wired into the engine — that's a future task; the file naming below matches what the audio system will look for.)

---

## ⭐ Defaults to render first

These two cover the player's first-run experience (Splash → Katy Trail). Render these; everything else is additive.

### `splash.ogg` — Home / Splash Screen
- **Use:** plays under the "SUBURBAN SCRAMBLE / Press Start" splash and the character-select screen
- **Duration:** 45 seconds (loopable)
- **Loops:** yes — render seamless

> **Prompt:** Nostalgic 16-bit chiptune title theme in C major, 100 BPM. Bright square-wave melody over a warm pulse-wave bass and a soft 8-bit drum kit (tick hi-hat, low kick, gated snare). Add a triumphant arpeggio rising every 8 bars and an airy chime pad in the background. Mood: bright suburban morning, slight retro adventure energy, hopeful but mischievous. No vocals. Seamless loop.

### `level_katy_trail.ogg` — Level 1: Katy Trail (Uptown)
- **Use:** plays while running the Katy Trail level
- **Duration:** 90 seconds (loopable)
- **Loops:** yes

> **Prompt:** Energetic 16-bit chiptune jog / synth-funk hybrid at 138 BPM in A minor. Driving 8-bit drum kit with a snappy snare on 2 and 4, percussive cowbell on the off-beats. Punchy pulse-wave bass groove. Lead is a bright square-wave with quick staccato runs that mimic footsteps. Layer a bell pluck arpeggio and an organ pad for the "morning sun on Uptown" feel. Mood: cardio, slightly competitive, playful tension — like jogging past too many influencers. No vocals. Seamless loop.

---

## Levels (full neighborhood loop)

### `level_driveway.ogg` — Level 0: Driveway Gauntlet (Tutorial)
- **Duration:** 60 seconds, looping
> **Prompt:** Gentle pixel-game tutorial theme, 95 BPM, C major. Soft xylophone melody, simple bouncy bass on the root, sparse triangle-wave drum kit. Mood: lazy Saturday morning, sprinklers ticking, paperboy in the distance — comfortable, almost a lullaby with a hint of comedy. Seamless loop, no vocals.

### `level_lower_greenville.ogg` — Level 2: Lower Greenville & M-Streets
- **Duration:** 100 seconds, looping
> **Prompt:** Indie-rock-meets-chiptune patio jam at 120 BPM in D major. Surfy chicken-pickin' guitar lead made of square waves, a tight pulse-wave bassline, claps on 2 and 4, and tinny bar-room piano stabs. Add subtle brunch chatter (low, indistinct synth pad mimicking a crowd). Mood: rosé-fueled patio energy, charming chaos, slight hangover. Seamless loop, no vocals.

### `level_highland_park.ogg` — Level 3: Highland Park HOA
- **Duration:** 100 seconds, looping
> **Prompt:** Elegant-but-sinister chiptune string quartet at 110 BPM in E minor. Pizzicato 8-bit strings playing a polite minor melody, plucked harpsichord-like bell counter-melody, gentle tympani thumps. Add an unsettling rising whole-tone run every 16 bars. Mood: too-perfect lawns, cold smiles, the HOA is watching. Seamless loop, no vocals.

### `level_evoque_run.ogg` — Level 4: Katie's Evoque Run (Katie-only driving level)
- **Duration:** 110 seconds, looping
> **Prompt:** High-energy synthwave / Outrun chiptune at 145 BPM in F# minor. Driving sidechained pulse-wave bass like a motorik kick pattern, gated reverb snare, layered FM-synth lead playing a soaring arpeggio melody. Add tape-hiss and a faint cassette wow-and-flutter. Mood: golden-hour Tollway drive in a white Range Rover with the windows down, Apple Watch pinging, slightly bratty confidence. Seamless loop, no vocals.

### `level_fourth_of_july.ogg` — Level 5: Fourth of July Panic
- **Duration:** 95 seconds, looping
> **Prompt:** Tense pixel-horror chiptune at 130 BPM in B minor. Pulsing low square-wave drone, off-beat tom hits, occasional dissonant high pluck like a distant firework warning. Sparse melody with tritone intervals. Add filtered crackle/boom samples (deep, sub-bass) every 4 bars. Mood: night, silhouettes of houses, sirens in the distance, a dog cowering in a closet. Seamless loop, no vocals.

### `level_northlake.ogg` — Level 6: Northlake & Justin (Final Level)
- **Duration:** 120 seconds, looping
> **Prompt:** Epic chiptune western-orchestral fusion at 100 BPM in D minor. Big triangle-wave brass-style theme, galloping pulse-wave bassline mimicking horse hooves, occasional whip-crack and metal clang percussion, tremolo string pad. A wide, open-prairie melody with a big modulating chorus every 32 bars. Mood: open range, water towers on the horizon, the storm is coming. Seamless loop, no vocals.

### `boss_default.ogg` — Generic Boss Theme (used when a level boss appears)
- **Duration:** 75 seconds, looping
> **Prompt:** Aggressive chiptune boss battle at 160 BPM in F minor. Distorted square-wave lead trading riffs with a deep pulse bass, double-time drum machine kit with rolling toms, dissonant minor-second stabs on the off-beats. Energetic, slightly camp villain energy. Seamless loop, no vocals.

### `boss_main_character.ogg` — Boss: The Main Character (Influencer, Katy Trail)
- **Duration:** 80 seconds, looping
> **Prompt:** Influencer-pop-meets-chiptune boss theme at 124 BPM in G minor. Sassy ducking sidechain bass, finger-snap percussion, FM-synth bell-pluck hook with a sing-songy taunt-shaped melody, occasional camera-shutter sample and faint TikTok-coded vocal chops (no real words). Mood: vain, flirty, completely unaware she's a boss. Seamless loop, no vocals.

---

## Character themes (short signature stings + loops)

These play on **Character Select** when the card is highlighted, and as a 4-bar intro sting on level start. Render two versions of each: a **30-second loop** (used during card hover and on the title screen) and a **5-second sting** (used on level start, victory pose, etc.).

### `theme_rosie.ogg` — Rosie (Border Collie, Tennis Ball Obsessive)
- **Duration:** 30s loop + 5s sting (render both)
> **Prompt:** Hyperactive chiptune at 165 BPM in E major. Rapid square-wave arpeggios racing up and down, snappy 8-bit drum loop, playful "yip-yip" pluck synth hook every 2 bars. Add a tennis-ball "boing" sample at the start of each phrase. Mood: pure border-collie ADHD, "where's the ball where's the ball where's the ball." No vocals.

### `theme_charlie.ogg` — Charlie (Tri-color Border Collie, Cul-de-sac Defender)
- **Duration:** 30s loop + 5s sting
> **Prompt:** Stoic chiptune theme at 80 BPM in C minor. Low square-wave bass walking line, slow noble triangle-wave melody like a Western-movie sheriff theme rendered in NES tones, gentle gated snare. Heavy on low end. Mood: dignified, patient, "I have been guarding this cul-de-sac for nine years and I will guard it for nine more." No vocals.

### `theme_katie.ogg` — Katie (The Walker, Pink Lululemon, Apple Watch)
- **Duration:** 30s loop + 5s sting
> **Prompt:** Bright pop-chiptune at 128 BPM in D major. Light pulse-wave melody, Apple-Watch-ping-style bell hits on the downbeat, breezy clap percussion, a single Apple Pay "ding" sample at the top of each loop. Mood: 10k steps, oat milk latte, pretending not to make eye contact with neighbors. No vocals.

### `theme_tia.ogg` — Tia (Older Confident Earl-Grey Cat)
- **Duration:** 30s loop + 5s sting
> **Prompt:** Cool jazzy chiptune at 95 BPM in F major. Slinky pulse-wave bass walking line, smooth triangle-wave melody with sliding pitch bends, brushed 8-bit hi-hat, occasional purring sub-bass throb. Mood: half-lidded, fully in control, "I was already on this windowsill." No vocals.

### `theme_nancy.ogg` — Nancy (Younger Skittish Earl-Grey Cat)
- **Duration:** 30s loop + 5s sting
> **Prompt:** Stutter-step chiptune at 150 BPM in B minor. Skittish staccato pulse-wave melody that breaks into fast 16th-note runs, then suddenly silent for half a bar before resuming. Tiny tympani rolls, jittery bell shimmer. Mood: zoomies-then-hides-under-the-couch, big-eyed adrenaline. No vocals.

---

## Game stings (one-shot, non-looping)

### `sting_game_over.ogg`
- **Duration:** 6 seconds
> **Prompt:** 16-bit chiptune game-over sting in C minor. Descending minor-third triplet motif on a square-wave lead resolving to a low pulse-wave thud, followed by a brief sad bell shimmer. No drums after the first beat. Mood: deflated, comedic loss, "we'll get it next time."

### `sting_victory.ogg`
- **Duration:** 8 seconds
> **Prompt:** Triumphant 16-bit chiptune victory fanfare in C major. Rising arpeggio on square-wave lead resolving to a sustained major chord, percussive timpani roll, sparkly chime tail. Mood: classic JRPG "you did it!" with a hint of suburban silliness — maybe a single dog-bark or cat-meow sample at the very end.

### `sting_dialogue_blip.ogg`
- **Duration:** 0.4 seconds
> **Prompt:** Single short pixel-game dialogue blip — a soft 8-bit pop, like the Pokémon text-advance sound. Mid-frequency pulse wave, very short, no decay tail.

### `sting_treat_pickup.ogg`
- **Duration:** 0.6 seconds
> **Prompt:** Quick rising chiptune coin / treat pickup sound. Three ascending square-wave notes (C5, E5, G5) with a tiny shimmer at the top. Bright and rewarding.

### `sting_frenzy_start.ogg`
- **Duration:** 1.2 seconds
> **Prompt:** Aggressive chiptune power-up sting. Distorted square-wave riser through an octave-and-a-half sweep into a thick gated chord stab with reverb tail. No vocals. Used when the player triggers Frenzy Mode.

---

## Recommended render order

1. `splash.ogg` *(highest priority — first thing the player hears)*
2. `level_katy_trail.ogg` *(only level shipping in v1)*
3. `boss_main_character.ogg` *(also v1)*
4. `sting_game_over.ogg` and `sting_victory.ogg` *(short, complete the loop)*
5. `theme_rosie.ogg`, `theme_katie.ogg` *(the two characters with custom dialogue in v1)*
6. The remaining character + level themes as Levels 2–6 are built.

---

## When ready to wire up audio

Drop the rendered files at `static/assets/audio/music/<id>.ogg`. The current `bridge` event bus is the right place to fire audio cues — add a `playMusic` / `playSting` event next to the existing `dialogue` / `gameOver` events and have a `<MusicHost />` Svelte component subscribe and manage `<audio>` elements. Engine code never needs to touch the audio layer directly.
