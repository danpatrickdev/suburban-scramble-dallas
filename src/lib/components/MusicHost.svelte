<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	interface Props {
		/** Filename under /assets/audio/music/, without extension. null = silence. */
		track: string | null;
		volume?: number; // 0..1, default 0.5
	}
	let { track, volume = 0.45 }: Props = $props();

	// Two <audio> elements so we can crossfade between tracks without a hard cut.
	let aA: HTMLAudioElement | null = $state(null);
	let aB: HTMLAudioElement | null = $state(null);
	let active = $state<'A' | 'B'>('A');
	let currentTrack = $state<string | null>(null);
	let unlocked = $state(false);

	const targetEl = $derived(active === 'A' ? aA : aB);
	const otherEl = $derived(active === 'A' ? aB : aA);

	let crossfadeTimer: ReturnType<typeof setInterval> | null = null;

	function startCrossfade(toEl: HTMLAudioElement, fromEl: HTMLAudioElement | null) {
		if (crossfadeTimer) clearInterval(crossfadeTimer);
		const fadeMs = 700;
		const tickMs = 30;
		const steps = fadeMs / tickMs;
		let step = 0;
		toEl.volume = 0;
		toEl.currentTime = 0;
		toEl.play().catch(() => {
			// Autoplay blocked; will retry on user gesture
		});
		crossfadeTimer = setInterval(() => {
			step++;
			const t = Math.min(1, step / steps);
			toEl.volume = volume * t;
			if (fromEl) fromEl.volume = volume * (1 - t);
			if (t >= 1) {
				if (fromEl) {
					fromEl.pause();
					fromEl.currentTime = 0;
				}
				if (crossfadeTimer) {
					clearInterval(crossfadeTimer);
					crossfadeTimer = null;
				}
			}
		}, tickMs);
	}

	$effect(() => {
		if (!aA || !aB) return;
		if (track === currentTrack) return;
		currentTrack = track;
		const next = track ? `/assets/audio/music/${track}.mp3` : null;
		const toEl = active === 'A' ? aB : aA;
		const fromEl = active === 'A' ? aA : aB;
		if (next) {
			toEl.src = next;
			toEl.loop = true;
			toEl.preload = 'auto';
			active = active === 'A' ? 'B' : 'A';
			if (unlocked) startCrossfade(toEl, fromEl);
		} else {
			fromEl.pause();
			fromEl.currentTime = 0;
		}
	});

	function unlock() {
		if (unlocked) return;
		unlocked = true;
		// Force-start the currently-active track on first interaction
		const el = active === 'A' ? aA : aB;
		if (el && el.src) startCrossfade(el, null);
	}

	onMount(() => {
		const handler = () => unlock();
		window.addEventListener('pointerdown', handler, { once: true });
		window.addEventListener('keydown', handler, { once: true });
		return () => {
			window.removeEventListener('pointerdown', handler);
			window.removeEventListener('keydown', handler);
		};
	});

	onDestroy(() => {
		if (crossfadeTimer) clearInterval(crossfadeTimer);
		aA?.pause();
		aB?.pause();
	});
</script>

<audio bind:this={aA} aria-hidden="true"></audio>
<audio bind:this={aB} aria-hidden="true"></audio>
