<script lang="ts">
	import { onMount } from 'svelte';

	let active = $state(false);

	onMount(() => {
		if (typeof window === 'undefined') return;
		active = new URLSearchParams(window.location.search).has('spine');
	});
</script>

{#if active}
	<div class="badge">
		<div class="row">
			<span class="dot"></span>
			<span class="label">SPINE TEST ACTIVE</span>
		</div>
		<div class="hint">Pick a character + difficulty to see Spineboy in-game</div>
	</div>
{/if}

<style>
	.badge {
		position: fixed;
		top: 12px;
		right: 12px;
		background: rgba(12, 14, 20, 0.95);
		border: 1px solid #88e1ff;
		padding: 8px 12px;
		font-size: 11px;
		color: #88e1ff;
		font-family: monospace;
		letter-spacing: 1px;
		z-index: 1000;
		pointer-events: none;
	}
	.row {
		display: flex;
		align-items: center;
		gap: 8px;
	}
	.dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #88e1ff;
		animation: pulse 1s infinite;
	}
	.label {
		font-weight: bold;
	}
	.hint {
		color: #888;
		font-size: 10px;
		margin-top: 4px;
		letter-spacing: 0.5px;
	}
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.3;
		}
	}
</style>
