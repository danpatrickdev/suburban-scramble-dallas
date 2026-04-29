import Phaser from 'phaser';
import { Player } from '../Player';
import type { GameScene } from '../../scenes/GameScene';
import { Projectile } from '../Projectile';

export class Nancy extends Player {
	constructor(scene: GameScene, x: number, y: number) {
		super(scene, x, y, 'nancy');
	}

	attack() {
		const scene = this.gameScene;
		// Fast triple-claw shotgun straight up
		const speed = 600;
		const offsets = [-12, 0, 12];
		for (const dx of offsets) {
			const p = new Projectile(scene, {
				x: this.x + dx,
				y: this.y - 14,
				vy: -speed,
				width: 14,
				height: 22,
				color: 0xffffff,
				color2: 0xffe2ec,
				shape: 'claw',
				damage: 2,
				pierce: false,
				lifetime: 700
			});
			scene.projectiles.add(p);
		}
	}

	special() {
		this.setStealth(true);
		this.setAlpha(0.4);
		this.scene.time.delayedCall(3000, () => {
			this.setStealth(false);
			this.setAlpha(1);
		});
	}
}
