import { Enemy } from '../Enemy';
import type { GameScene } from '../../scenes/GameScene';

export class Coffee extends Enemy {
	private hasSlipped = false;

	constructor(scene: GameScene, x: number, y: number) {
		super(scene, x, y, 'enemy_coffee', 'coffee', 99, 0); // can't be killed; just an obstacle
		// Sprite is 48×48 — circular puddle hitbox centered on the cup splat.
		this.body.setCircle(18, 6, 6);
		this.play('enemy_coffee__idle');
	}

	tick(_deltaSec: number, scrollSpeed: number) {
		this.body.setVelocity(0, scrollSpeed);
	}

	onPlayerOverlap() {
		if (this.hasSlipped) return;
		this.hasSlipped = true;
		this.gameScene.input_.slipFor(800);
		this.setTintFill(0xfff5a8);
		this.scene.time.delayedCall(200, () => this.clearTint());
	}
}
