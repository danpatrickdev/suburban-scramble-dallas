// Typed event bus connecting the Phaser game (canvas) to Svelte UI overlays.
// Phaser emits gameplay events; Svelte responds (and vice-versa for resume signals).

import type { CharacterId, DialogueLine } from './types';

type Handler<T> = (payload: T) => void;

class TypedEmitter<Events extends Record<string, unknown>> {
	private listeners = new Map<keyof Events, Set<Handler<unknown>>>();

	on<K extends keyof Events>(event: K, handler: Handler<Events[K]>): () => void {
		let set = this.listeners.get(event);
		if (!set) {
			set = new Set();
			this.listeners.set(event, set);
		}
		set.add(handler as Handler<unknown>);
		return () => set!.delete(handler as Handler<unknown>);
	}

	emit<K extends keyof Events>(event: K, payload: Events[K]): void {
		const set = this.listeners.get(event);
		if (!set) return;
		for (const h of set) (h as Handler<Events[K]>)(payload);
	}

	clear(): void {
		this.listeners.clear();
	}
}

export interface BridgeEvents {
	hpChange: { hp: number; max: number };
	distanceChange: { distance: number };
	comboChange: { combo: number; frenzy: boolean };
	specialReady: { ready: boolean };
	dialogue: DialogueLine | null;
	gameOver: { distance: number; character: CharacterId; victory: boolean };
	resumeFromDialogue: undefined;
	requestPause: undefined;
	requestResume: undefined;
}

export const bridge = new TypedEmitter<BridgeEvents & Record<string, unknown>>();
