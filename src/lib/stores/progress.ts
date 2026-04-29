import { writable } from 'svelte/store';
import type { CharacterId, LevelId } from '$lib/game/types';
import { STORAGE_KEYS } from '$lib/game/constants';

export interface Progress {
	unlockedCharacters: CharacterId[];
	highScores: Partial<Record<LevelId, Partial<Record<CharacterId, number>>>>;
	totalTreats: number;
}

const defaultProgress: Progress = {
	unlockedCharacters: ['rosie', 'katie', 'charlie', 'nancy', 'tia'],
	highScores: {},
	totalTreats: 0
};

function load(): Progress {
	if (typeof localStorage === 'undefined') return defaultProgress;
	try {
		const unlocked = JSON.parse(localStorage.getItem(STORAGE_KEYS.unlockedCharacters) || 'null');
		const highScores = JSON.parse(localStorage.getItem(STORAGE_KEYS.highScores) || '{}');
		const totalTreats = Number(localStorage.getItem(STORAGE_KEYS.totalTreats) || '0');
		return {
			unlockedCharacters: Array.isArray(unlocked) && unlocked.length > 0 ? unlocked : defaultProgress.unlockedCharacters,
			highScores,
			totalTreats: Number.isFinite(totalTreats) ? totalTreats : 0
		};
	} catch {
		return defaultProgress;
	}
}

export const progress = writable<Progress>(defaultProgress);

if (typeof window !== 'undefined') {
	progress.set(load());
	progress.subscribe((p) => {
		try {
			localStorage.setItem(STORAGE_KEYS.unlockedCharacters, JSON.stringify(p.unlockedCharacters));
			localStorage.setItem(STORAGE_KEYS.highScores, JSON.stringify(p.highScores));
			localStorage.setItem(STORAGE_KEYS.totalTreats, String(p.totalTreats));
		} catch {
			/* non-fatal */
		}
	});
}

export function refreshFromStorage() {
	if (typeof window === 'undefined') return;
	progress.set(load());
}
