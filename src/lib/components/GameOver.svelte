<script lang="ts">
	import { CHARACTER_NAMES } from '$lib/game/data/characters';
	import type { CharacterId } from '$lib/game/types';

	interface Props {
		distance: number;
		character: CharacterId;
		victory: boolean;
		best: number;
		onretry: () => void;
		onhome: () => void;
	}
	let { distance, character, victory, best, onretry, onhome }: Props = $props();

	const newBest = $derived(distance >= best);

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ' ') onretry();
		if (e.key === 'Escape') onhome();
	}
</script>

<svelte:window onkeydown={handleKey} />

<div class="over fade-in">
	<div class="panel">
		<div class="title" class:victory>
			{victory ? 'YOU WIN' : 'GAME OVER'}
		</div>
		<div class="character">{CHARACTER_NAMES[character]}</div>
		<div class="distance">
			<div class="num">{distance}m</div>
			<div class="label">distance</div>
		</div>
		{#if newBest}
			<div class="new-best blink">NEW HIGH SCORE</div>
		{:else}
			<div class="best">best: {best}m</div>
		{/if}
		<div class="actions">
			<button class="btn primary" onclick={onretry}>Retry (Enter)</button>
			<button class="btn" onclick={onhome}>Character Select (Esc)</button>
		</div>
	</div>
</div>

<style>
	.over {
		position: absolute;
		inset: 0;
		background: rgba(12, 14, 20, 0.95);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 40;
	}
	.panel {
		background: #14182a;
		border: 2px solid #ff3b5c;
		padding: 32px 40px;
		text-align: center;
		display: flex;
		flex-direction: column;
		gap: 16px;
		min-width: 280px;
	}
	.title {
		font-size: 28px;
		letter-spacing: 6px;
		color: #ff3b5c;
	}
	.title.victory {
		color: #ffd500;
		border-color: #ffd500;
	}
	.character {
		color: #f8b6cb;
		letter-spacing: 3px;
	}
	.distance {
		margin: 8px 0;
	}
	.num {
		font-size: 48px;
		color: #ffd500;
		font-weight: 900;
	}
	.label {
		font-size: 11px;
		color: #888;
		letter-spacing: 2px;
	}
	.new-best {
		color: #ffd500;
		font-size: 12px;
		letter-spacing: 3px;
	}
	.best {
		color: #888;
		font-size: 11px;
	}
	.actions {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-top: 8px;
	}
	.btn {
		background: transparent;
		border: 1px solid #444;
		color: #ccc;
		padding: 8px 16px;
		font-size: 12px;
		letter-spacing: 2px;
	}
	.btn.primary {
		border-color: #f8b6cb;
		color: #f8b6cb;
	}
	.btn.primary:hover {
		background: #f8b6cb;
		color: #0c0e14;
	}
	.btn:hover {
		background: #2a2f48;
	}
</style>
