import Phaser from 'phaser';
import { Player } from '../Player';
import type { GameScene } from '../../scenes/GameScene';
import { Projectile } from '../Projectile';

export class Tia extends Player {
	constructor(scene: GameScene, x: number, y: number) {
		super(scene, x, y, 'tia');
	}

	attack() {
		const scene = this.gameScene;
		// Wide tail-whip arc that sweeps forward
		const p = new Projectile(scene, {
			x: this.x,
			y: this.y - 14,
			vy: -440,
			width: 56,
			height: 22,
			color: 0xfaf089,
			color2: 0xffffff,
			shape: 'arc',
			damage: 2,
			pierce: true,
			maxHits: 5,
			lifetime: 1100
		});
		scene.projectiles.add(p);
	}

	special() {
		this.makeInvulnerable(1000);
		this.scene.tweens.add({
			targets: this,
			scale: 1.5,
			y: this.y - 12,
			duration: 500,
			yoyo: true,
			ease: 'Sine.easeInOut'
		});
	}
}
