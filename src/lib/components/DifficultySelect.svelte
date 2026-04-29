<script lang="ts">
	import { DIFFICULTIES, DIFFICULTY_ORDER, type DifficultyId } from '$lib/game/data/difficulty';
	import { difficulty } from '$lib/stores/difficulty';

	interface Props {
		oncontinue: () => void;
		onback: () => void;
	}
	let { oncontinue, onback }: Props = $props();

	let focusedIdx = $state(DIFFICULTY_ORDER.indexOf($difficulty));
	const focused = $derived(DIFFICULTY_ORDER[focusedIdx]);

	function pick(id: DifficultyId) {
		difficulty.set(id);
		oncontinue();
	}

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
			focusedIdx = (focusedIdx + 1) % DIFFICULTY_ORDER.length;
		} else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
			focusedIdx = (focusedIdx - 1 + DIFFICULTY_ORDER.length) % DIFFICULTY_ORDER.length;
		} else if (e.key === 'Enter' || e.key === ' ') {
			pick(focused);
		} else if (e.key === 'Escape') {
			onback();
		}
	}
</script>

<svelte:window onkeydown={handleKey} />

<div class="diff fade-in">
	<header>
		<button class="back" onclick={onback}>← Back</button>
		<h2>Pick your scramble level</h2>
		<div class="spacer"></div>
	</header>

	<div class="grid">
		{#each DIFFICULTY_ORDER as id, i (id)}
			{@const d = DIFFICULTIES[id]}
			<button
				class="card"
				class:focused={i === focusedIdx}
				style:--accent={d.color}
				onmouseenter={() => (focusedIdx = i)}
				onclick={() => pick(id)}
			>
				<div class="label">{d.label}</div>
				<div class="tagline">{d.tagline}</div>
				<div class="stats">
					<span>Enemies <b>×{d.enemyCountMult.toFixed(1)}</b></span>
					<span>Speed <b>×{d.enemySpeedMult.toFixed(2)}</b></span>
					<span>Spawn rate <b>×{d.waveFrequencyMult.toFixed(1)}</b></span>
					{#if d.playerHpBonus > 0}
						<span class="bonus">+{d.playerHpBonus} HP</span>
					{/if}
				</div>
			</button>
		{/each}
	</div>

	<div class="hint">← → to scroll · Enter to start · Esc to back out</div>
</div>

<style>
	.diff {
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
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
		width: min(900px, 100%);
	}
	.card {
		background: #14182a;
		border: 2px solid #2a2f48;
		padding: 18px 14px;
		display: flex;
		flex-direction: column;
		gap: 8px;
		text-align: left;
		color: var(--ink);
		transition: transform 100ms, border-color 100ms, box-shadow 100ms;
	}
	.card.focused {
		border-color: var(--accent);
		transform: translateY(-3px);
		box-shadow: 0 4px 0 #0c0e14;
	}
	.label {
		font-size: 18px;
		letter-spacing: 3px;
		color: var(--accent);
	}
	.tagline {
		font-size: 12px;
		color: #ccc;
		min-height: 32px;
	}
	.stats {
		display: flex;
		flex-direction: column;
		gap: 3px;
		font-size: 11px;
		color: #888;
	}
	.stats b {
		color: #ffd500;
	}
	.bonus {
		color: #88e1ff;
	}
	.hint {
		color: #555;
		font-size: 10px;
		letter-spacing: 2px;
	}
	@media (max-width: 700px) {
		.grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
</style>
