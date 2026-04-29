<script lang="ts">
	import { onMount } from 'svelte';
	import { bridge } from '$lib/game/PhaserBridge';
	import { CHARACTER_NAMES } from '$lib/game/data/characters';
	import type { CharacterId } from '$lib/game/types';

	interface Props {
		character: CharacterId;
	}
	let { character }: Props = $props();

	let hp = $state(3);
	let max = $state(3);
	let distance = $state(0);
	let combo = $state(0);
	let frenzy = $state(false);
	let specialReady = $state(true);
	let popKey = $state(0);

	onMount(() => {
		const offHp = bridge.on('hpChange', ({ hp: h, max: m }) => {
			if (h < hp) popKey++;
			hp = h;
			max = m;
		});
		const offDist = bridge.on('distanceChange', ({ distance: d }) => (distance = d));
		const offCombo = bridge.on('comboChange', ({ combo: c, frenzy: f }) => {
			combo = c;
			frenzy = f;
		});
		const offSpc = bridge.on('specialReady', ({ ready }) => (specialReady = ready));
		return () => {
			offHp();
			offDist();
			offCombo();
			offSpc();
		};
	});
</script>

<div class="hud">
	<div class="row top">
		<div class="hearts" data-pop={popKey}>
			{#each Array(max) as _, i (i)}
				<span class="heart" class:lost={i >= hp}>♥</span>
			{/each}
		</div>
		<div class="character">{CHARACTER_NAMES[character]}</div>
		<div class="distance">{distance}m</div>
	</div>
	<div class="row bottom">
		<div class="combo" class:frenzy>
			{#if frenzy}
				<span>FRENZY!</span>
			{:else if combo > 0}
				<span>{combo}× combo</span>
			{:else}
				<span class="dim">—</span>
			{/if}
		</div>
		<div class="special" class:ready={specialReady}>
			{specialReady ? 'SPECIAL: SHIFT' : 'SPECIAL …'}
		</div>
	</div>
</div>

<style>
	.hud {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		padding: 10px 12px;
		display: flex;
		flex-direction: column;
		gap: 6px;
		pointer-events: none;
		font-size: 12px;
		z-index: 10;
		text-shadow: 1px 1px 0 #000;
	}
	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.hearts {
		display: flex;
		gap: 2px;
		font-size: 22px;
		animation: heart-pop 250ms ease-out;
		animation-iteration-count: 0;
	}
	.hearts[data-pop] {
		animation-iteration-count: 1;
	}
	.heart {
		color: #ff3b5c;
	}
	.heart.lost {
		color: #333;
	}
	.character {
		color: #f8b6cb;
		letter-spacing: 2px;
	}
	.distance {
		color: #ffd500;
	}
	.combo {
		color: #888;
		letter-spacing: 1px;
	}
	.combo.frenzy {
		color: #ff3b5c;
		font-weight: 900;
		animation: blink 500ms infinite;
	}
	.combo .dim {
		opacity: 0.4;
	}
	.special {
		color: #555;
		letter-spacing: 1px;
	}
	.special.ready {
		color: #88e1ff;
	}
</style>
