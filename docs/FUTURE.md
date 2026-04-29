# Future Plans

Running list of features and content planned for after the current build. Trim entries as they ship.

## New levels

### Stockyards (Fort Worth) — planned

A Fort Worth Stockyards-themed level. Counter-balances the Uptown / Highland Park / Northlake DFW lineup with a true western district.

**Visual direction**
- Old wooden boardwalks, brick storefronts with vintage signage
- Cattle pens fencing along edges
- Honky-tonk neon (think Billy-Bob's-style without naming it), pool-hall windows, neon longhorn silhouettes
- Sunset/dusk palette: orange, dusty pink, warm shadows
- Background details: water tower, historic train depot, distant stockyard chutes

**Enemies**
- **Stampeding Longhorn** — large, fast, charges in a straight line. Telegraphs with a ground-rumble cue
- **Boot-Scoot Tourist** — slow but moves in groups doing a synchronized line dance pattern
- **Honky-Tonk Bouncer** — slow patroller with a wide hitbox; hard to dodge in narrow passages
- **Beer-Bottle Toss** — projectile thrown from a saloon doorway, parabolic arc
- **Rodeo Clown** — fast and erratic, mid-tier mini-boss

**Boss**
- **The Mechanical Bull** — center-screen rotating arena. Player has to land hits during predictable spin patterns and avoid the kicking back legs. Phase 2 it accelerates and starts sparking. Phase 3 it throws sparks in arcs.

**Music prompt seed (for ElevenLabs later)**
> Texas honky-tonk crossover instrumental at 118 BPM in E major. Twangy slide-guitar riff, walking upright bass, brushed snare, hand claps, a tasteful fiddle counter-melody. Big rolling toms in the chorus. Modern production polish — slight sidechain pump, airy reverb. Mood: dusty Stockyards at golden hour, neon flickering on, cowboy boots on a wooden boardwalk, swagger with a wink. Instrumental only — no lyrics. Seamless loop.

**Implementation notes**
- New file under `src/lib/game/data/levels/stockyards.ts` defining waves, dialogue, boss key
- Register in `LEVELS` and append `'stockyards'` to `LEVEL_ORDER` in `src/lib/game/data/levels/index.ts`
- New scenery props: cattle pens, honky-tonk neon signs, water tower, train depot, hay bales
- New tile asset: dusty boardwalk + dirt-road tile (extend `scripts/aseprite/characters.lua`)

## Other ideas (parking lot)

- **Tornado Siren final boss** for `northlake` — already in the spec, needs implementation
- **Treat Bag upgrade shop** between runs — spend treats on permanent stat buffs
- **Photo Album** — gallery of defeated bosses with dialogue snippets, unlocks as you beat them
- **Daily challenge mode** — fixed seed, leaderboard
- **Audio sting hooks** — wire `bridge.playSting('treatPickup')` etc. into the existing event bus once the audio host supports one-shots alongside the music host
