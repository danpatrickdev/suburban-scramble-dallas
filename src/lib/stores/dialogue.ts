import { writable } from 'svelte/store';
import type { DialogueLine } from '$lib/game/types';
import { bridge } from '$lib/game/PhaserBridge';

export const currentDialogue = writable<DialogueLine | null>(null);

if (typeof window !== 'undefined') {
	bridge.on('dialogue', (line) => {
		currentDialogue.set(line);
	});
}

export function dismissDialogue() {
	currentDialogue.set(null);
	bridge.emit('resumeFromDialogue', undefined);
}
