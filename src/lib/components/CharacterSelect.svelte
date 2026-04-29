<script lang="ts">
	import { CHARACTER_BLURBS, CHARACTER_IDS, CHARACTER_NAMES, CHARACTER_STATS } from '$lib/game/data/characters';
	import type { CharacterId } from '$lib/game/types';
	import { selectedCharacter } from '$lib/stores/character';
	import { progress } from '$lib/stores/progress';

	interface Props {
		onselect: (id: CharacterId) => void;
		onback: () => void;
	}
	let { onselect, onback }: Props = $props();

	let hoveredId = $state<CharacterId | null>(null);
	let focusedIdx = $state(0);

	const focused = $derived(CHARACTER_IDS[focusedIdx]);
	const stats = $derived(CHARACTER_STATS[focused]);
	const blurb = $derived(CHARACTER_BLURBS[focused]);

	function bestScore(id: CharacterId): number {
		return $progress.highScores.katy_trail?.[id] ?? 0;
	}

	function pick(id: CharacterId) {
		selectedCharacter.set(id);
		onselect(id);
	}

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
			focusedIdx = (focusedIdx + 1) % CHARACTER_IDS.length;
		} else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
			focusedIdx = (focusedIdx - 1 + CHARACTER_IDS.length) % CHARACTER_IDS.length;
		} else if (e.key === 'Enter' || e.key === ' ') {
			pick(focused);
		} else if (e.key === 'Escape') {
			onback();
		}
	}
</script>

<svelte:window onkeydown={handleKey} />

<div class="select fade-in">
	<header>
		<button class="back" onclick={onback}>← Back</button>
		<h2>Pick your scramble</h2>
		<div class="spacer"></div>
	</header>

	<div class="grid">
		{#each CHARACTER_IDS as id, i (id)}
			<button
				class="card"
				class:focused={i === focusedIdx}
				class:hovered={hoveredId === id}
				onmouseenter={() => {
					hoveredId = id;
					focusedIdx = i;
				}}
				onmouseleave={() => (hoveredId = null)}
				onclick={() => pick(id)}
			>
				<div class="portrait">
					<img src={`assets/ui/portraits/${id}.png`} alt={CHARACTER_NAMES[id]} />
				</div>
				<div class="name">{CHARACTER_NAMES[id]}</div>
				<div class="best">Best: {bestScore(id)}</div>
			</button>
		{/each}
	</div>

	<div class="info">
		<div class="info-name">{CHARACTER_NAMES[focused]}</div>
		<div class="info-blurb">{blurb}</div>
		<div class="info-stats">
			<span>SPD <b>{stats.speed.toFixed(1)}x</b></span>
			<span>HP <b>{stats.hp}</b></span>
			<span>ATK <b>{stats.attack}</b></span>
			<span>SPC <b>{stats.special}</b></span>
		</div>
	</div>

	<div class="hint">← → to scroll · Enter to walk · Esc to back out</div>
</div>

<style>
	.select {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 24px;
		padding: 24px;
		box-sizing: border-box;
	}
	header {
		display: flex;
		align-items: center;
		gap: 16px;
		width: min(900px, 100%);
		justify-content: space-between;
	}
	header h2 {
		margin: 0;
		color: #f8b6cb;
		letter-spacing: 4px;
	}
	.back {
		background: transparent;
		border: 1px solid #444;
		color: #aaa;
		padding: 4px 10px;
		font-size: 12px;
	}
	.spacer {
		width: 70px;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		gap: 16px;
		width: min(900px, 100%);
	}
	.card {
		background: #14182a;
		border: 2px solid #2a2f48;
		color: var(--ink);
		padding: 14px 8px 10px;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		transition: transform 100ms, border-color 100ms, box-shadow 100ms;
	}
	.card.focused,
	.card.hovered {
		border-color: #f8b6cb;
		transform: translateY(-3px);
		box-shadow: 0 4px 0 #2a1828;
	}
	.portrait {
		width: 144px;
		height: 144px;
		image-rendering: pixelated;
		background: #0c0e14;
		border: 1px solid #2a2f48;
	}
	.portrait img {
		width: 100%;
		height: 100%;
		image-rendering: pixelated;
	}
	.name {
		font-size: 16px;
		letter-spacing: 2px;
		color: #f1f5f9;
		margin-top: 2px;
	}
	.best {
		font-size: 11px;
		color: #888;
		letter-spacing: 1px;
	}
	.info {
		width: min(900px, 100%);
		min-height: 100px;
		background: #14182a;
		border: 1px solid #2a2f48;
		padding: 14px;
	}
	.info-name {
		font-size: 18px;
		color: #f8b6cb;
		letter-spacing: 2px;
		margin-bottom: 6px;
	}
	.info-blurb {
		color: #ccc;
		font-size: 13px;
		margin-bottom: 12px;
	}
	.info-stats {
		display: flex;
		gap: 16px;
		flex-wrap: wrap;
		font-size: 11px;
		color: #aaa;
	}
	.info-stats b {
		color: #ffd500;
	}
	.hint {
		color: #555;
		font-size: 10px;
		letter-spacing: 2px;
	}
	@media (max-width: 640px) {
		.grid {
			grid-template-columns: repeat(3, 1fr);
		}
	}
</style>
