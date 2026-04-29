import Phaser from 'phaser';
import type { GameScene } from '../scenes/GameScene';
import { GAME_HEIGHT, GAME_WIDTH } from '../constants';
import { bridge } from '../PhaserBridge';

export class MainCharacterBoss extends Phaser.Physics.Arcade.Sprite {
	private maxHp: number;
	hp: number;
	private phoneOffset = { x: 18, y: -10 };
	private phoneHitRadius = 14;
	private dir = 1;
	private spawnTimer = 0;
	private settled = false;

	declare body: Phaser.Physics.Arcade.Body;

	constructor(scene: GameScene, hpMult = 1) {
		super(scene, GAME_WIDTH / 2, -60, 'boss_main_character', 'idle_0');
		this.maxHp = Math.max(4, Math.round(12 * hpMult));
		this.hp = this.maxHp;
		scene.add.existing(this);
		scene.physics.add.existing(this);
		this.setDepth(8);
		this.body.setSize(48, 48).setOffset(8, 8);
		this.play('boss_main_character__idle');
	}

	phoneX(): number {
		return this.x + this.phoneOffset.x;
	}
	phoneY(): number {
		return this.y + this.phoneOffset.y;
	}

	hitPhone(damage: number) {
		this.hp -= damage;
		this.setTintFill(0xffffff);
		this.scene.time.delayedCall(80, () => this.clearTint());
		bridge.emit('hpChange', { hp: Math.max(0, Math.ceil(this.hp)), max: this.maxHp });
		if (this.hp <= 0) {
			(this.scene as GameScene).onBossDefeated();
		}
	}

	tick(deltaSec: number, _scrollSpeed: number) {
		if (!this.settled) {
			// Slide down to the upper third of the screen
			this.y += 60 * deltaSec;
			if (this.y >= GAME_HEIGHT * 0.28) {
				this.settled = true;
				bridge.emit('hpChange', { hp: this.maxHp, max: this.maxHp });
			}
			return;
		}
		// Pendulum sway across screen
		this.x += this.dir * 80 * deltaSec;
		if (this.x < 60) {
			this.x = 60;
			this.dir = 1;
		}
		if (this.x > GAME_WIDTH - 60) {
			this.x = GAME_WIDTH - 60;
			this.dir = -1;
		}
		// Spawn followers periodically
		this.spawnTimer += deltaSec;
		if (this.spawnTimer >= 4) {
			this.spawnTimer = 0;
			(this.scene as GameScene).spawnFollower(this.x, this.y + 30);
		}
		// Visualize phone hitbox
		const ring = (this.scene as GameScene).bossPhoneRing;
		if (ring) ring.setPosition(this.phoneX(), this.phoneY());
	}
}
