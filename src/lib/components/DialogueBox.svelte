<script lang="ts">
	import { currentDialogue, dismissDialogue } from '$lib/stores/dialogue';
	import { onMount } from 'svelte';

	let displayText = $state('');
	let typing = $state(false);
	let charIdx = $state(0);
	let timer: ReturnType<typeof setInterval> | null = null;

	$effect(() => {
		const line = $currentDialogue;
		if (!line) {
			displayText = '';
			typing = false;
			charIdx = 0;
			if (timer) {
				clearInterval(timer);
				timer = null;
			}
			return;
		}
		// Start typing effect
		displayText = '';
		charIdx = 0;
		typing = true;
		if (timer) clearInterval(timer);
		timer = setInterval(() => {
			charIdx++;
			displayText = line.text.slice(0, charIdx);
			if (charIdx >= line.text.length) {
				typing = false;
				if (timer) {
					clearInterval(timer);
					timer = null;
				}
			}
		}, 30);
	});

	function advance() {
		const line = $currentDialogue;
		if (!line) return;
		if (typing) {
			// Skip typing — show full text
			displayText = line.text;
			charIdx = line.text.length;
			typing = false;
			if (timer) {
				clearInterval(timer);
				timer = null;
			}
			return;
		}
		dismissDialogue();
	}

	function handleKey(e: KeyboardEvent) {
		if (!$currentDialogue) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			advance();
		}
	}

	onMount(() => () => {
		if (timer) clearInterval(timer);
	});
</script>

<svelte:window onkeydown={handleKey} />

{#if $currentDialogue}
	<button class="dialogue-wrap" onclick={advance} aria-label="Advance dialogue">
		<div class="dialogue">
			<div class="portrait">
				<img src={$currentDialogue.portrait} alt="portrait" />
			</div>
			<div class="text">
				<div class="speaker">{$currentDialogue.character.toUpperCase()}</div>
				<div class="body">{displayText}{#if typing}<span class="cursor">_</span>{/if}</div>
				{#if !typing}
					<div class="advance blink">▼ ENTER</div>
				{/if}
			</div>
		</div>
	</button>
{/if}

<style>
	.dialogue-wrap {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 16px;
		z-index: 20;
		cursor: pointer;
		background: transparent;
		border: 0;
		text-align: left;
		font: inherit;
		color: inherit;
		display: block;
		width: 100%;
	}
	.dialogue {
		background: rgba(12, 14, 20, 0.95);
		border: 2px solid #f8b6cb;
		padding: 14px;
		display: flex;
		gap: 14px;
		min-height: 96px;
		box-shadow: 4px 4px 0 #000;
	}
	.portrait {
		width: 80px;
		height: 80px;
		flex-shrink: 0;
		background: #1a1f3a;
		border: 1px solid #2a2f48;
		image-rendering: pixelated;
	}
	.portrait img {
		width: 100%;
		height: 100%;
		image-rendering: pixelated;
		object-fit: cover;
	}
	.text {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4px;
		font-size: 13px;
		color: #f1f5f9;
	}
	.speaker {
		font-size: 10px;
		letter-spacing: 3px;
		color: #f8b6cb;
	}
	.body {
		flex: 1;
		line-height: 1.4;
	}
	.cursor {
		opacity: 0.6;
	}
	.advance {
		font-size: 10px;
		color: #ffd500;
		text-align: right;
	}
</style>
