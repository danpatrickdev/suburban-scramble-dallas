import Phaser from 'phaser';
import { Player } from '../Player';
import type { GameScene } from '../../scenes/GameScene';
import { Projectile } from '../Projectile';

export class Charlie extends Player {
	constructor(scene: GameScene, x: number, y: number) {
		super(scene, x, y, 'charlie');
	}

	attack() {
		const scene = this.gameScene;
		// Slow-moving wide shockwaves — three rolling rocks marching up
		scene.cameras.main.shake(80, 0.005);
		const speed = 320;
		const offsets = [-50, 0, 50];
		for (const dx of offsets) {
			const p = new Projectile(scene, {
				x: this.x + dx,
				y: this.y - 12,
				vy: -speed,
				width: 36,
				height: 18,
				color: 0x7b4a1e,
				color2: 0xc8a070,
				shape: 'shockwave',
				damage: 3,
				pierce: true,
				maxHits: 4,
				lifetime: 1400
			});
			scene.projectiles.add(p);
		}
	}

	special() {
		this.setStationary(true);
		this.setDamageReduction(0.9, 3000);
		const shield = this.scene.add.rectangle(this.x, this.y, 36, 36, 0x7b4a1e, 0.25).setStrokeStyle(2, 0x7b4a1e, 1);
		shield.setDepth(9);
		this.scene.tweens.add({
			targets: shield,
			alpha: 0,
			duration: 3000,
			onUpdate: () => shield.setPosition(this.x, this.y),
			onComplete: () => {
				shield.destroy();
				this.setStationary(false);
			}
		});
	}
}
