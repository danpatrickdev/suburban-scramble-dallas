import Phaser from 'phaser';
import { Player } from '../Player';
import type { GameScene } from '../../scenes/GameScene';
import { Projectile } from '../Projectile';

export class Rosie extends Player {
	constructor(scene: GameScene, x: number, y: number) {
		super(scene, x, y, 'rosie');
	}

	attack() {
		const scene = this.gameScene;
		// Three forward-traveling sonic bark waves in a tight spread
		const speed = 460;
		const spread = [
			{ angle: 0,        damage: 1 },
			{ angle: -0.18,    damage: 1 },
			{ angle: 0.18,     damage: 1 }
		];
		for (const s of spread) {
			const p = new Projectile(scene, {
				x: this.x + Math.sin(s.angle) * 6,
				y: this.y - 14,
				vx: Math.sin(s.angle) * speed,
				vy: -Math.cos(s.angle) * speed,
				width: 28,
				height: 14,
				color: 0xfff5a8,
				color2: 0xffe066,
				shape: 'bark',
				damage: s.damage,
				pierce: true,
				maxHits: 3,
				lifetime: 1100,
				growth: 1.4
			});
			scene.projectiles.add(p);
		}
	}

	special() {
		this.boostSpeed(2.0, 3000);
		const trail = this.scene.add.particles(this.x, this.y, 'char_rosie', {
			frame: 'idle_0',
			lifespan: 200,
			alpha: { start: 0.5, end: 0 },
			scale: { start: 0.6, end: 0.2 },
			follow: this,
			frequency: 30
		});
		this.scene.time.delayedCall(3000, () => trail.destroy());
	}
}
