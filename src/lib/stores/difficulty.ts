import { writable } from 'svelte/store';
import type { DifficultyId } from '$lib/game/data/difficulty';

const KEY = 'ssd:difficulty';

function readInitial(): DifficultyId {
	if (typeof localStorage === 'undefined') return 'intermediate';
	const v = localStorage.getItem(KEY);
	if (v === 'beginner' || v === 'intermediate' || v === 'hard' || v === 'x_games') return v;
	return 'intermediate';
}

export const difficulty = writable<DifficultyId>(readInitial());

difficulty.subscribe((v) => {
	if (typeof localStorage === 'undefined') return;
	localStorage.setItem(KEY, v);
});
