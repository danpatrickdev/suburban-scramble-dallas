import { writable } from 'svelte/store';
import type { CharacterId } from '$lib/game/types';
import { STORAGE_KEYS } from '$lib/game/constants';

function readLast(): CharacterId {
	if (typeof localStorage === 'undefined') return 'rosie';
	const v = localStorage.getItem(STORAGE_KEYS.lastCharacter);
	const valid: CharacterId[] = ['rosie', 'katie', 'charlie', 'nancy', 'tia'];
	return (valid.includes(v as CharacterId) ? v : 'rosie') as CharacterId;
}

export const selectedCharacter = writable<CharacterId>(readLast());

selectedCharacter.subscribe((v) => {
	if (typeof localStorage === 'undefined') return;
	localStorage.setItem(STORAGE_KEYS.lastCharacter, v);
});
