import type { CharacterId } from './types';
import type { DifficultyId } from './data/difficulty';
import { GAME_HEIGHT, GAME_WIDTH } from './constants';

export interface RunningGame {
	destroy(): void;
}

function spineTestEnabled(): boolean {
	if (typeof window === 'undefined') return false;
	return new URLSearchParams(window.location.search).has('spine');
}

export async function startGame(
	parent: HTMLElement,
	character: CharacterId,
	difficulty: DifficultyId = 'intermediate'
): Promise<RunningGame> {
	const Phaser = (await import('phaser')).default;
	// spine-phaser's require-shim expects window.Phaser to exist BEFORE the
	// module is imported (it was designed for <script> inclusion). Set it.
	if (typeof window !== 'undefined') {
		(window as unknown as { Phaser: typeof Phaser }).Phaser = Phaser;
	}
	const { BootScene } = await import('./scenes/BootScene');
	const { GameScene } = await import('./scenes/GameScene');
	const useSpine = spineTestEnabled();
	const SpinePluginModule = useSpine ? await import('@esotericsoftware/spine-phaser') : null;

	if (useSpine) {
		console.log('[spine] window.Phaser set, plugin module:', SpinePluginModule ? 'loaded' : 'missing');
		console.log('[spine] SpinePlugin export:', typeof (SpinePluginModule as { SpinePlugin?: unknown })?.SpinePlugin);
	}

	const config: Phaser.Types.Core.GameConfig = {
		// spine-phaser's WebGL renderer path is the supported one. Force WEBGL when in spine mode.
		type: useSpine ? Phaser.WEBGL : Phaser.AUTO,
		parent,
		width: GAME_WIDTH,
		height: GAME_HEIGHT,
		backgroundColor: '#0c0e14',
		// Pixel-art mode globally crisps up sprites; with Spine we want smooth vector
		// scaling. Default to pixel-art unless ?spine is in the URL.
		pixelArt: !useSpine,
		antialias: useSpine,
		roundPixels: !useSpine,
		scale: {
			mode: Phaser.Scale.FIT,
			autoCenter: Phaser.Scale.CENTER_BOTH
		},
		physics: {
			default: 'arcade',
			arcade: { gravity: { x: 0, y: 0 }, debug: false }
		},
		fps: { target: 60, forceSetTimeOut: false },
		scene: [BootScene, GameScene],
		plugins: useSpine && SpinePluginModule
			? {
				scene: [
					{
						key: 'spine.SpinePlugin',
						plugin: SpinePluginModule.SpinePlugin,
						mapping: 'spine'
					}
				]
			}
			: undefined
	};

	const game = new Phaser.Game(config);
	game.registry.set('character', character);
	game.registry.set('difficulty', difficulty);
	game.registry.set('spineTest', useSpine);

	return {
		destroy() {
			game.destroy(true);
		}
	};
}
