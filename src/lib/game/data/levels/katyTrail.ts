import type { LevelDef } from '../../types';
import { KATY_TRAIL_LENGTH_MS, KATY_TRAIL_SPEED_MOD } from '../../constants';

export const katyTrail: LevelDef = {
	id: 'katy_trail',
	title: 'Katy Trail — Uptown',
	tileKey: 'tile_katy_trail',
	tilePath: 'assets/tiles/katy_trail.png',
	speedMod: KATY_TRAIL_SPEED_MOD,
	durationMs: KATY_TRAIL_LENGTH_MS,
	bossKey: 'main_character',
	waves: [
		{ at: 5_000, kind: 'peloton', count: 2, pattern: 'line' },
		{ at: 10_000, kind: 'coffee', count: 1, pattern: 'random' },
		{ at: 15_000, kind: 'leash', count: 1 },
		{ at: 22_000, kind: 'peloton', count: 3, pattern: 'spread' },
		{ at: 28_000, kind: 'coffee', count: 2, pattern: 'random' },
		{ at: 35_000, kind: 'leash', count: 1 },
		{ at: 42_000, kind: 'peloton', count: 4, pattern: 'line' },
		{ at: 50_000, kind: 'coffee', count: 2, pattern: 'spread' },
		{ at: 58_000, kind: 'leash', count: 1 },
		{ at: 65_000, kind: 'peloton', count: 5, pattern: 'spread' },
		{ at: 72_000, kind: 'coffee', count: 3, pattern: 'random' },
		{ at: 80_000, kind: 'peloton', count: 4, pattern: 'line' }
	],
	dialogue: [
		{
			at: -1,
			character: 'rosie',
			line: {
				character: 'rosie',
				portrait: 'assets/ui/portraits/rosie.png',
				text: 'Tennis ball... I smell it. Hold my leash.'
			}
		},
		{
			at: -1,
			character: 'katie',
			line: {
				character: 'katie',
				portrait: 'assets/ui/portraits/katie.png',
				text: 'Ugh, can everyone just stay on their side of the yellow line?'
			}
		},
		{
			at: 45_000,
			line: {
				character: 'enemy',
				portrait: 'assets/ui/portraits/rosie.png',
				text: '! Influencer ahead. Phone out. Trail blocked.'
			}
		},
		{
			at: -2,
			line: {
				character: 'enemy',
				portrait: 'assets/bosses/main_character.png',
				text: 'OMG do NOT come into my shot right now—'
			}
		}
	]
};
