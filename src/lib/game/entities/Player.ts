import Phaser from 'phaser';
import { CHARACTER_STATS } from '../data/characters';
import {
	ATTACK_COOLDOWN,
	GAME_HEIGHT,
	GAME_WIDTH,
	PLAYER_BASE_SPEED,
	PLAYER_HITBOX_RADIUS,
	SPECIAL_COOLDOWN
} from '../constants';
import type { CharacterId } from '../types';
import { bridge } from '../PhaserBridge';
import type { GameScene } from '../scenes/GameScene';

export abstract class Player extends Phaser.Physics.Arcade.Sprite {
	readonly characterId: CharacterId;
	readonly maxHp: number;
	hp: number;
	speedMultiplier: number;

	private attackCooldownUntil = 0;
	private specialCooldownUntil = 0;
	private invulnerableUntil = 0;
	private speedBoostUntil = 0;
	private speedBoostMult = 1;
	protected damageReduction = 0;
	protected stationary = false;
	protected stealth = false;
	protected frenzyActive = false;

	declare body: Phaser.Physics.Arcade.Body;

	constructor(scene: GameScene, x: number, y: number, characterId: CharacterId) {
		super(scene, x, y, `char_${characterId}`, 'idle_0');
		this.characterId = characterId;
		const stats = CHARACTER_STATS[characterId];
		this.maxHp = stats.hp;
		this.hp = stats.hp;
		this.speedMultiplier = stats.speed;

		scene.add.existing(this);
		scene.physics.add.existing(this);
		this.setDepth(10);
		this.body.setCircle(PLAYER_HITBOX_RADIUS, 16 - PLAYER_HITBOX_RADIUS, 18 - PLAYER_HITBOX_RADIUS);
		this.body.setCollideWorldBounds(true);

		this.play(`char_${characterId}__idle`);
		bridge.emit('hpChange', { hp: this.hp, max: this.maxHp });
	}

	get gameScene(): GameScene {
		return this.scene as GameScene;
	}

	tickMovement(dx: number, dy: number) {
		if (this.stationary) {
			this.body.setVelocity(0, 0);
			return;
		}
		const len = Math.hypot(dx, dy) || 1;
		const nx = dx / len;
		const ny = dy / len;
		const moving = dx !== 0 || dy !== 0;
		const speedBoost = this.scene.time.now < this.speedBoostUntil ? this.speedBoostMult : 1;
		const speed = PLAYER_BASE_SPEED * this.speedMultiplier * speedBoost;
		this.body.setVelocity(moving ? nx * speed : 0, moving ? ny * speed : 0);
		this.setFlipX(nx < -0.05);
		const animKey = `char_${this.characterId}__${moving ? 'walk' : 'idle'}`;
		if (this.anims.currentAnim?.key !== animKey) this.play(animKey, true);
	}

	tryAttack(now: number): boolean {
		const cd = this.frenzyActive ? 60 : ATTACK_COOLDOWN;
		if (now < this.attackCooldownUntil) return false;
		this.attackCooldownUntil = now + cd;
		this.play(`char_${this.characterId}__attack`, true);
		this.attack();
		return true;
	}

	trySpecial(now: number): boolean {
		const cd = this.frenzyActive ? 0 : SPECIAL_COOLDOWN;
		if (now < this.specialCooldownUntil && !this.frenzyActive) return false;
		this.specialCooldownUntil = now + cd;
		this.play(`char_${this.characterId}__special`, true);
		this.special();
		this.emitSpecialReady();
		return true;
	}

	emitSpecialReady() {
		const ready = this.scene.time.now >= this.specialCooldownUntil;
		bridge.emit('specialReady', { ready });
	}

	takeDamage(amount = 1) {
		if (this.scene.time.now < this.invulnerableUntil) return;
		const final = Math.max(0, amount - this.damageReduction);
		if (final <= 0) return;
		this.hp -= final;
		this.makeInvulnerable(700);
		this.flashDamage();
		this.gameScene.cameras.main.shake(120, 0.005);
		bridge.emit('hpChange', { hp: this.hp, max: this.maxHp });
		this.gameScene.combo.onHit();
		if (this.hp <= 0) this.gameScene.endRun(false);
	}

	heal(amount: number) {
		this.hp = Math.min(this.maxHp, this.hp + amount);
		bridge.emit('hpChange', { hp: this.hp, max: this.maxHp });
	}

	applyHpBonus(extra: number) {
		(this as { maxHp: number }).maxHp = this.maxHp + extra;
		this.hp = this.maxHp;
		bridge.emit('hpChange', { hp: this.hp, max: this.maxHp });
	}

	makeInvulnerable(ms: number) {
		this.invulnerableUntil = Math.max(this.invulnerableUntil, this.scene.time.now + ms);
	}

	private flashDamage() {
		this.setTintFill(0xffffff);
		this.scene.time.delayedCall(80, () => this.clearTint());
	}

	protected boostSpeed(mult: number, ms: number) {
		this.speedBoostMult = mult;
		this.speedBoostUntil = this.scene.time.now + ms;
	}

	protected setStationary(stationary: boolean) {
		this.stationary = stationary;
	}

	protected setDamageReduction(amount: number, ms: number) {
		this.damageReduction = amount;
		this.scene.time.delayedCall(ms, () => {
			this.damageReduction = 0;
		});
	}

	protected setStealth(stealth: boolean) {
		this.stealth = stealth;
	}

	isStealthed(): boolean {
		return this.stealth;
	}

	setFrenzy(active: boolean) {
		this.frenzyActive = active;
	}

	abstract attack(): void;
	abstract special(): void;
}
