<script lang="ts">
	import { bridge } from '$lib/game/PhaserBridge';

	interface Props {
		open: boolean;
		onresume: () => void;
		onquit: () => void;
	}
	let { open, onresume, onquit }: Props = $props();

	function resume() {
		bridge.emit('requestResume', undefined);
		onresume();
	}

	function handleKey(e: KeyboardEvent) {
		if (!open) return;
		if (e.key === 'Escape') {
			e.preventDefault();
			resume();
		}
	}
</script>

<svelte:window onkeydown={handleKey} />

{#if open}
	<div class="pause">
		<div class="panel">
			<div class="title">PAUSED</div>
			<button class="btn" onclick={resume}>Resume</button>
			<button class="btn quit" onclick={onquit}>Quit Run</button>
			<div class="hint">Esc to resume</div>
		</div>
	</div>
{/if}

<style>
	.pause {
		position: absolute;
		inset: 0;
		background: rgba(12, 14, 20, 0.85);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 30;
	}
	.panel {
		background: #14182a;
		border: 2px solid #f8b6cb;
		padding: 28px 36px;
		display: flex;
		flex-direction: column;
		gap: 12px;
		min-width: 220px;
		text-align: center;
	}
	.title {
		font-size: 22px;
		letter-spacing: 4px;
		color: #f8b6cb;
		margin-bottom: 8px;
	}
	.btn {
		background: transparent;
		border: 1px solid #f8b6cb;
		color: #f8b6cb;
		padding: 8px 16px;
		font-size: 14px;
		letter-spacing: 2px;
	}
	.btn:hover {
		background: #f8b6cb;
		color: #0c0e14;
	}
	.btn.quit {
		border-color: #ff3b5c;
		color: #ff3b5c;
	}
	.btn.quit:hover {
		background: #ff3b5c;
		color: #0c0e14;
	}
	.hint {
		font-size: 10px;
		color: #555;
		margin-top: 8px;
		letter-spacing: 2px;
	}
</style>
