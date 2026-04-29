import Phaser from 'phaser';
import {
	BASE_SCROLL_SPEED,
	GAME_HEIGHT,
	GAME_WIDTH,
	MAX_SCROLL_SPEED,
	SCROLL_RAMP_PER_SEC
} from '../constants';

export class ScrollingBackground {
	private scene: Phaser.Scene;
	private tile: Phaser.GameObjects.TileSprite;
	private speed: number;
	private speedMod: number;

	constructor(scene: Phaser.Scene, tileKey: string, speedMod: number) {
		this.scene = scene;
		this.speedMod = speedMod;
		this.speed = BASE_SCROLL_SPEED * speedMod;
		this.tile = scene.add
			.tileSprite(0, 0, GAME_WIDTH, GAME_HEIGHT, tileKey)
			.setOrigin(0, 0)
			.setDepth(-1000);
	}

	update(deltaSeconds: number, elapsedSeconds: number) {
		const targetBase = Math.min(BASE_SCROLL_SPEED + SCROLL_RAMP_PER_SEC * elapsedSeconds, MAX_SCROLL_SPEED);
		this.speed = targetBase * this.speedMod;
		this.tile.tilePositionY -= this.speed * deltaSeconds;
	}

	currentSpeed(): number {
		return this.speed;
	}
}
