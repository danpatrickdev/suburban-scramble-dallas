import Phaser from 'phaser';
import type { GameScene } from '../scenes/GameScene';
import type { Enemy } from './Enemy';

export type ProjectileShape = 'bark' | 'laser' | 'shockwave' | 'claw' | 'arc';

export interface ProjectileOptions {
	x: number;
	y: number;
	vx?: number;
	vy: number;
	width: number;
	height: number;
	color: number;
	color2?: number;
	shape: ProjectileShape;
	damage: number;
	pierce?: boolean;        // if true, doesn't despawn on hit
	maxHits?: number;        // limit pierce; default Infinity if pierce=true
	lifetime?: number;       // ms; default 1500
	growth?: number;         // px/sec growth (sonic bark expanding); default 0
	tailLength?: number;     // for laser/claw motion trail
}

// A single shooter-style projectile. Uses an unmanaged Graphics object so we
// don't need pre-rendered sprites for each attack visual.
export class Projectile extends Phaser.GameObjects.Container {
	declare body: Phaser.Physics.Arcade.Body;
	private gfx: Phaser.GameObjects.Graphics;
	private opts: ProjectileOptions;
	private hitsRemaining: number;
	private hitSet = new Set<Enemy>();
	private spawnedAt: number;
	private currentWidth: number;
	private currentHeight: number;
	readonly damage: number;

	constructor(scene: GameScene, opts: ProjectileOptions) {
		super(scene, opts.x, opts.y);
		this.opts = opts;
		this.damage = opts.damage;
		this.hitsRemaining = opts.maxHits ?? (opts.pierce ? Infinity : 1);
		this.spawnedAt = scene.time.now;
		this.currentWidth = opts.width;
		this.currentHeight = opts.height;

		this.gfx = scene.add.graphics();
		this.add(this.gfx);
		scene.add.existing(this);
		scene.physics.add.existing(this);

		this.body.setSize(opts.width, opts.height);
		this.body.setOffset(-opts.width / 2, -opts.height / 2);
		this.body.setVelocity(opts.vx ?? 0, opts.vy);
		this.body.setAllowGravity(false);

		this.setDepth(7);
		this.draw();
	}

	get scene_(): GameScene {
		return this.scene as GameScene;
	}

	private draw() {
		const { color, color2, shape } = this.opts;
		const w = this.currentWidth;
		const h = this.currentHeight;
		this.gfx.clear();
		switch (shape) {
			case 'bark': {
				// expanding semi-circle wave
				this.gfx.lineStyle(3, color, 1);
				this.gfx.strokeEllipse(0, 0, w, h);
				this.gfx.lineStyle(2, color2 ?? 0xffffff, 0.8);
				this.gfx.strokeEllipse(0, 0, w * 0.7, h * 0.7);
				break;
			}
			case 'laser': {
				// thin red beam with bright core
				this.gfx.fillStyle(color, 0.7);
				this.gfx.fillRect(-w / 2, -h / 2, w, h);
				this.gfx.fillStyle(color2 ?? 0xffffff, 1);
				this.gfx.fillRect(-w / 4, -h / 2, w / 2, h);
				break;
			}
			case 'shockwave': {
				// thick stone-colored rolling wave
				this.gfx.fillStyle(color, 0.9);
				this.gfx.fillEllipse(0, 0, w, h);
				this.gfx.lineStyle(2, color2 ?? 0xffffff, 0.7);
				this.gfx.strokeEllipse(0, 0, w, h);
				// inner rocks
				this.gfx.fillStyle(color2 ?? 0xffffff, 0.6);
				this.gfx.fillCircle(-w / 4, 0, 2);
				this.gfx.fillCircle(w / 4, 0, 2);
				break;
			}
			case 'claw': {
				// three parallel slash lines
				this.gfx.lineStyle(2, color, 1);
				const sl = h / 2;
				for (let i = -1; i <= 1; i++) {
					this.gfx.beginPath();
					this.gfx.moveTo(i * (w / 4), -sl);
					this.gfx.lineTo(i * (w / 4) + 2, sl);
					this.gfx.strokePath();
				}
				this.gfx.fillStyle(color2 ?? 0xffffff, 0.4);
				this.gfx.fillRect(-w / 2, -h / 4, w, h / 2);
				break;
			}
			case 'arc': {
				// crescent / arc swipe
				this.gfx.fillStyle(color, 0.5);
				this.gfx.fillEllipse(0, 0, w, h);
				this.gfx.fillStyle(color2 ?? 0xffffff, 0.7);
				this.gfx.fillEllipse(0, h / 4, w * 0.85, h * 0.5);
				break;
			}
		}
	}

	preUpdate(time: number, delta: number) {
		const elapsed = time - this.spawnedAt;
		const lifetime = this.opts.lifetime ?? 1500;

		// Growth (e.g. sonic bark expanding ring)
		if (this.opts.growth) {
			const factor = 1 + (this.opts.growth * elapsed) / 1000;
			this.currentWidth = this.opts.width * factor;
			this.currentHeight = this.opts.height * factor;
			this.body.setSize(this.currentWidth, this.currentHeight);
			this.body.setOffset(-this.currentWidth / 2, -this.currentHeight / 2);
			this.draw();
		}

		// Off-screen / lifetime cleanup
		if (elapsed >= lifetime || this.y < -100 || this.y > this.scene_.cameras.main.height + 100) {
			this.destroy();
		}
	}

	tryHit(enemy: Enemy): boolean {
		if (this.hitSet.has(enemy)) return false;
		this.hitSet.add(enemy);
		this.hitsRemaining -= 1;
		if (this.hitsRemaining <= 0) {
			this.scene.time.delayedCall(20, () => this.destroy());
		}
		return true;
	}
}
