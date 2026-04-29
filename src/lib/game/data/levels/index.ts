import type { LevelDef, LevelId } from '../../types';
import { katyTrail } from './katyTrail';

export const LEVELS: Partial<Record<LevelId, LevelDef>> = {
	katy_trail: katyTrail
};

export const LEVEL_ORDER: LevelId[] = [
	'driveway',
	'katy_trail',
	'lower_greenville',
	'highland_park',
	'evoque_run',
	'fourth_of_july',
	'northlake'
	// Future: 'stockyards' — Fort Worth Stockyards level. Western/honky-tonk vibe,
	// stampeding longhorns as enemies, mechanical-bull or rodeo-clown boss.
	// See docs/FUTURE.md.
];

export function getLevel(id: LevelId): LevelDef {
	const lvl = LEVELS[id];
	if (!lvl) throw new Error(`Level "${id}" is not implemented yet.`);
	return lvl;
}
