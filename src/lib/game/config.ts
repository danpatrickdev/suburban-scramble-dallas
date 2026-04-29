import type Phaser from 'phaser';
import { GAME_HEIGHT, GAME_WIDTH } from './constants';

export function buildConfig(parent: HTMLElement, scenes: Phaser.Types.Core.GameConfig['scene']): Phaser.Types.Core.GameConfig {
	return {
		type: 1, // Phaser.AUTO; resolved at runtime by Phaser
		parent,
		width: GAME_WIDTH,
		height: GAME_HEIGHT,
		backgroundColor: '#0c0e14',
		pixelArt: true,
		antialias: false,
		roundPixels: true,
		scale: {
			mode: 3, // Phaser.Scale.FIT
			autoCenter: 1 // Phaser.Scale.CENTER_BOTH
		},
		physics: {
			default: 'arcade',
			arcade: {
				gravity: { x: 0, y: 0 },
				debug: false
			}
		},
		fps: { target: 60, forceSetTimeOut: false },
		scene: scenes
	};
}
