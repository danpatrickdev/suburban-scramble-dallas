<script lang="ts">
	interface Props {
		onstart: () => void;
	}
	let { onstart }: Props = $props();

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ' ') onstart();
	}
</script>

<svelte:window onkeydown={handleKey} />

<div class="splash fade-in">
	<div class="title">
		<div class="line-1">SUBURBAN</div>
		<div class="line-2">SCRAMBLE</div>
		<div class="subtitle">Dallas Edition</div>
	</div>
	<button class="start" onclick={onstart}>
		<span class="blink">▶ PRESS START</span>
	</button>
	<div class="hint">Enter / Space / Click</div>
</div>

<style>
	.splash {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 32px;
		background: radial-gradient(circle at 50% 30%, #1a1f3a 0%, #0c0e14 70%);
	}
	.title {
		text-align: center;
		line-height: 0.95;
	}
	.line-1,
	.line-2 {
		font-size: clamp(48px, 8vw, 96px);
		font-weight: 900;
		letter-spacing: 4px;
		color: #f8b6cb;
		text-shadow: 4px 4px 0 #000, 8px 8px 0 #1a1a2a;
	}
	.line-2 {
		color: #ffd500;
	}
	.subtitle {
		font-size: clamp(14px, 1.6vw, 22px);
		letter-spacing: 6px;
		margin-top: 16px;
		color: #aaa;
	}
	.start {
		background: transparent;
		border: 2px solid #f8b6cb;
		color: #f8b6cb;
		padding: 12px 28px;
		font-size: 18px;
		letter-spacing: 2px;
	}
	.start:hover {
		background: #f8b6cb;
		color: #0c0e14;
	}
	.hint {
		color: #555;
		font-size: 11px;
		letter-spacing: 3px;
	}
</style>
