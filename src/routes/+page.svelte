<script lang="ts">
	import Splash from '$lib/components/Splash.svelte';
	import CharacterSelectView from '$lib/components/CharacterSelect.svelte';
	import DifficultySelect from '$lib/components/DifficultySelect.svelte';
	import GameContainer from '$lib/components/GameContainer.svelte';
	import HUD from '$lib/components/HUD.svelte';
	import DialogueBox from '$lib/components/DialogueBox.svelte';
	import PauseMenu from '$lib/components/PauseMenu.svelte';
	import GameOver from '$lib/components/GameOver.svelte';
	import MusicHost from '$lib/components/MusicHost.svelte';
	import { selectedCharacter } from '$lib/stores/character';
	import { progress, refreshFromStorage } from '$lib/stores/progress';
	import { currentDialogue } from '$lib/stores/dialogue';
	import { difficulty } from '$lib/stores/difficulty';
	import { bridge } from '$lib/game/PhaserBridge';
	import { onMount } from 'svelte';
	import type { CharacterId } from '$lib/game/types';

	type Phase = 'splash' | 'select' | 'difficulty' | 'playing' | 'gameover';

	let phase = $state<Phase>('splash');
	let runKey = $state(0);
	let paused = $state(false);
	let result = $state<{ distance: number; character: CharacterId; victory: boolean } | null>(null);

	const playingCharacter = $derived($selectedCharacter);
	const playingDifficulty = $derived($difficulty);
	const bestForCharacter = $derived(
		($progress.highScores.katy_trail?.[playingCharacter] as number | undefined) ?? 0
	);

	function startSplash() {
		phase = 'select';
	}
	function pickedCharacter(_id: CharacterId) {
		phase = 'difficulty';
	}
	function startRun() {
		refreshFromStorage();
		paused = false;
		result = null;
		runKey++;
		phase = 'playing';
	}
	function backToSplash() {
		phase = 'splash';
	}

	onMount(() => {
		const offGameOver = bridge.on('gameOver', (r) => {
			result = r;
			refreshFromStorage();
			setTimeout(() => {
				phase = 'gameover';
			}, 350);
		});
		const offPause = bridge.on('requestPause', () => {
			if (phase === 'playing') paused = true;
		});
		const offResume = bridge.on('requestResume', () => {
			if (phase === 'playing') paused = false;
		});
		return () => {
			offGameOver();
			offPause();
			offResume();
		};
	});

	function retry() {
		startRun();
	}
	function homeFromGameOver() {
		phase = 'select';
	}
	function quitRun() {
		paused = false;
		result = null;
		phase = 'select';
	}

	$effect(() => {
		if (phase !== 'playing' && $currentDialogue) currentDialogue.set(null);
	});

	const musicTrack = $derived(
		phase === 'playing' ? 'level_katy_trail'
		: phase === 'gameover' ? null
		: 'splash'
	);
</script>

<MusicHost track={musicTrack} />

<div class="root">
	{#if phase === 'splash'}
		<Splash onstart={startSplash} />
	{:else if phase === 'select'}
		<CharacterSelectView onselect={pickedCharacter} onback={backToSplash} />
	{:else if phase === 'difficulty'}
		<DifficultySelect oncontinue={startRun} onback={() => (phase = 'select')} />
	{:else if phase === 'playing'}
		{#key runKey}
			<GameContainer character={playingCharacter} difficulty={playingDifficulty} />
		{/key}
		<HUD character={playingCharacter} />
		<DialogueBox />
		<PauseMenu open={paused} onresume={() => (paused = false)} onquit={quitRun} />
	{:else if phase === 'gameover' && result}
		<GameOver
			distance={result.distance}
			character={result.character}
			victory={result.victory}
			best={bestForCharacter}
			onretry={retry}
			onhome={homeFromGameOver}
		/>
	{/if}
</div>

<style>
	.root {
		position: absolute;
		inset: 0;
	}
</style>
