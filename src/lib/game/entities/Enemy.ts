import Phaser from 'phaser';
import type { GameScene } from '../scenes/GameScene';
import type { EnemyKind } from '../types';

export abstract class Enemy extends Phaser.Physics.Arcade.Sprite {
	hp: number;
	readonly kind: EnemyKind;
	readonly contactDamage: number;
	private stunUntil = 0;

	declare body: Phaser.Physics.Arcade.Body;

	constructor(scene: GameScene, x: number, y: number, textureKey: string, kind: EnemyKind, hp: number, contactDamage = 1) {
		super(scene, x, y, textureKey, 'idle_0');
		this.kind = kind;
		this.hp = hp;
		this.contactDamage = contactDamage;
		scene.add.existing(this);
		scene.physics.add.existing(this);
		this.setDepth(5);
		// Render enemies bigger than their atlas frames — they were reading too
		// small once characters got Spine-rigged at full size.
		this.setScale(1.5);
		const animKey = `${textureKey}__idle`;
		if (scene.anims.exists(animKey)) this.play(animKey);
	}

	get gameScene(): GameScene {
		return this.scene as GameScene;
	}

	stun(ms: number) {
		this.stunUntil = Math.max(this.stunUntil, this.scene.time.now + ms);
		this.setTintFill(0xddddff);
		this.scene.time.delayedCall(80, () => this.clearTint());
	}

	isStunned(): boolean {
		return this.scene.time.now < this.stunUntil;
	}

	takeHit(damage: number) {
		this.hp -= damage;
		this.setTintFill(0xffffff);
		this.scene.time.delayedCall(60, () => this.clearTint());
		if (this.hp <= 0) this.kill();
	}

	kill() {
		this.gameScene.combo.onKill();
		// Death poof
		const poof = this.scene.add.circle(this.x, this.y, 8, 0xffffff, 0.7);
		poof.setDepth(6);
		this.scene.tweens.add({
			targets: poof,
			radius: 18,
			alpha: 0,
			duration: 220,
			onComplete: () => poof.destroy()
		});
		this.destroy();
	}

	abstract tick(deltaSec: number, scrollSpeed: number): void;

	preUpdate(time: number, delta: number) {
		super.preUpdate(time, delta);
	}
}
