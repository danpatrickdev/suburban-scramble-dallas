import type { CharacterId } from './types';
import type { DifficultyId } from './data/difficulty';
import { GAME_HEIGHT, GAME_WIDTH } from './constants';

export interface RunningGame {
	destroy(): void;
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
	const SpinePluginModule = await import('@esotericsoftware/spine-phaser');

	const config: Phaser.Types.Core.GameConfig = {
		type: Phaser.WEBGL,
		parent,
		width: GAME_WIDTH,
		height: GAME_HEIGHT,
		backgroundColor: '#0c0e14',
		// Smooth scaling for Spine vector parts; the trail tile and remaining
		// pixel art read fine without nearest-neighbor.
		pixelArt: false,
		antialias: true,
		roundPixels: false,
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
		plugins: {
			scene: [
				{
					key: 'spine.SpinePlugin',
					plugin: SpinePluginModule.SpinePlugin,
					mapping: 'spine'
				}
			]
		}
	};

	const game = new Phaser.Game(config);
	game.registry.set('character', character);
	game.registry.set('difficulty', difficulty);
	game.registry.set('spineModule', SpinePluginModule);

	return {
		destroy() {
			game.destroy(true);
		}
	};
}
