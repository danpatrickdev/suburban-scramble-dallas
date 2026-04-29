<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { startGame, type RunningGame } from '$lib/game/PhaserGame';
	import type { CharacterId } from '$lib/game/types';
	import type { DifficultyId } from '$lib/game/data/difficulty';

	interface Props {
		character: CharacterId;
		difficulty: DifficultyId;
	}
	let { character, difficulty }: Props = $props();

	let host: HTMLDivElement | null = $state(null);
	let running: RunningGame | null = null;

	onMount(async () => {
		if (!host) return;
		running = await startGame(host, character, difficulty);
	});

	onDestroy(() => {
		running?.destroy();
		running = null;
	});
</script>

<div class="canvas-host" bind:this={host}></div>

<style>
	/* Phaser handles canvas centering itself via Scale.CENTER_BOTH; keep this
	   parent as a plain block container so Phaser's margin-auto positioning
	   works. Adding flex/grid here fights Phaser's positioning. */
	.canvas-host {
		position: absolute;
		inset: 0;
		background: #000;
		overflow: hidden;
	}
	:global(.canvas-host canvas) {
		image-rendering: pixelated;
		image-rendering: crisp-edges;
		display: block;
	}
</style>
