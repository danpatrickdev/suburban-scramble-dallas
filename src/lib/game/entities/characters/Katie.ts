import Phaser from 'phaser';
import { Player } from '../Player';
import type { GameScene } from '../../scenes/GameScene';
import { Projectile } from '../Projectile';

export class Katie extends Player {
	constructor(scene: GameScene, x: number, y: number) {
		super(scene, x, y, 'katie');
	}

	attack() {
		const scene = this.gameScene;
		// Single fast piercing laser straight up from the watch
		const p = new Projectile(scene, {
			x: this.x + 6,
			y: this.y - 16,
			vy: -900,
			width: 5,
			height: 28,
			color: 0xff3030,
			color2: 0xffffff,
			shape: 'laser',
			damage: 2,
			pierce: true,
			maxHits: 99,
			lifetime: 800
		});
		scene.projectiles.add(p);
		// Brief muzzle flash on the watch
		const flash = scene.add.circle(this.x + 6, this.y - 4, 6, 0xff8888, 0.9).setDepth(8);
		scene.tweens.add({
			targets: flash,
			alpha: 0,
			scale: 1.6,
			duration: 120,
			onComplete: () => flash.destroy()
		});
	}

	special() {
		this.makeInvulnerable(2000);
		const bubble = this.scene.add.circle(this.x, this.y, 22, 0x88e1ff, 0.3).setStrokeStyle(2, 0x88e1ff, 0.8);
		bubble.setDepth(9);
		this.scene.tweens.add({
			targets: bubble,
			alpha: 0,
			duration: 2000,
			onUpdate: () => bubble.setPosition(this.x, this.y),
			onComplete: () => bubble.destroy()
		});
	}
}
