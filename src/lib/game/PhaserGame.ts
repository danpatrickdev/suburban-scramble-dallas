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
	const { BootScene } = await import('./scenes/BootScene');
	const { GameScene } = await import('./scenes/GameScene');

	const config: Phaser.Types.Core.GameConfig = {
		type: Phaser.AUTO,
		parent,
		width: GAME_WIDTH,
		height: GAME_HEIGHT,
		backgroundColor: '#0c0e14',
		pixelArt: true,
		antialias: false,
		roundPixels: true,
		scale: {
			mode: Phaser.Scale.FIT,
			autoCenter: Phaser.Scale.CENTER_BOTH
		},
		physics: {
			default: 'arcade',
			arcade: { gravity: { x: 0, y: 0 }, debug: false }
		},
		fps: { target: 60, forceSetTimeOut: false },
		scene: [BootScene, GameScene]
	};

	const game = new Phaser.Game(config);
	game.registry.set('character', character);
	game.registry.set('difficulty', difficulty);

	return {
		destroy() {
			game.destroy(true);
		}
	};
}
