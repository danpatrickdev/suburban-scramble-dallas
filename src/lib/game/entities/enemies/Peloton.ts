import { Enemy } from '../Enemy';
import type { GameScene } from '../../scenes/GameScene';

export class Peloton extends Enemy {
	private targetVelY: number;

	constructor(scene: GameScene, x: number, y: number, scrollSpeed: number) {
		super(scene, x, y, 'enemy_peloton', 'peloton', 1, 1);
		// Pelotons rocket past the player faster than the world scrolls.
		this.targetVelY = scrollSpeed + 140;
		// Sprite is 48×48 — keep a slightly forgiving collision box centered on the rider.
		this.body.setSize(30, 38).setOffset(9, 5);
		this.play('enemy_peloton__walk');
	}

	tick(_deltaSec: number, scrollSpeed: number) {
		if (this.isStunned()) {
			this.body.setVelocity(0, scrollSpeed);
			return;
		}
		this.targetVelY = scrollSpeed + 140;
		this.body.setVelocity(0, this.targetVelY);
	}
}
