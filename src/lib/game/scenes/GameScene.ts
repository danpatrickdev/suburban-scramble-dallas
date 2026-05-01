import Phaser from 'phaser';
import { bridge } from '../PhaserBridge';
import { ScrollingBackground } from '../systems/ScrollingBackground';
import { Scenery } from '../systems/Scenery';
import { InputController } from '../systems/InputController';
import { EnemyFactory } from '../systems/EnemyFactory';
import { LevelManager } from '../systems/LevelManager';
import { ComboSystem } from '../systems/ComboSystem';
import { katyTrail } from '../data/levels/katyTrail';
import { GAME_HEIGHT, GAME_WIDTH, STORAGE_KEYS } from '../constants';
import type { CharacterId } from '../types';
import { DIFFICULTIES, type DifficultyId } from '../data/difficulty';
import { Player } from '../entities/Player';
import { Rosie } from '../entities/characters/Rosie';
import { Katie } from '../entities/characters/Katie';
import { Charlie } from '../entities/characters/Charlie';
import { Nancy } from '../entities/characters/Nancy';
import { Tia } from '../entities/characters/Tia';
import { MainCharacterBoss } from '../entities/Boss';
import { Peloton } from '../entities/enemies/Peloton';
import { Coffee } from '../entities/enemies/Coffee';
import type { Enemy } from '../entities/Enemy';
import { Projectile } from '../entities/Projectile';

type SpineCharacterObject = Phaser.GameObjects.GameObject & {
	x: number;
	y: number;
	active: boolean;
	visible: boolean;
	alpha: number;
	setPosition: (x: number, y: number) => unknown;
	setScale: (s: number) => unknown;
	setDepth: (d: number) => unknown;
	setVisible: (v: boolean) => unknown;
	setAlpha: (a: number) => unknown;
	setActive: (a: boolean) => unknown;
	animationState?: {
		setAnimation: (track: number, name: string, loop: boolean) => unknown;
		tracks?: Array<{ animation?: { name?: string } }>;
	};
};

export class GameScene extends Phaser.Scene {
	background!: ScrollingBackground;
	scenery!: Scenery;
	input_!: InputController;
	factory!: EnemyFactory;
	level!: LevelManager;
	combo!: ComboSystem;

	player!: Player;
	enemies!: Phaser.GameObjects.Group;
	coffees!: Phaser.GameObjects.Group;
	projectiles!: Phaser.GameObjects.Group;
	boss?: MainCharacterBoss;
	bossPhoneRing?: Phaser.GameObjects.Arc;

	difficulty!: DifficultyId;

	private characterId!: CharacterId;
	private prevTime = 0;
	private ended = false;
	private cleanupHandlers: Array<() => void> = [];

	constructor() {
		super('Game');
	}

	create() {
		this.ended = false;
		this.characterId = (this.registry.get('character') as CharacterId) ?? 'rosie';
		this.difficulty = (this.registry.get('difficulty') as DifficultyId) ?? 'intermediate';
		const mod = DIFFICULTIES[this.difficulty];

		this.background = new ScrollingBackground(this, katyTrail.tileKey, katyTrail.speedMod * mod.enemySpeedMult);
		this.scenery = new Scenery(this);
		this.input_ = new InputController(this);
		this.factory = new EnemyFactory(this);
		this.level = new LevelManager(this, katyTrail, this.characterId, mod);
		this.combo = new ComboSystem(this);

		this.enemies = this.add.group({ runChildUpdate: false });
		this.coffees = this.add.group({ runChildUpdate: false });
		this.projectiles = this.add.group();

		this.player = this.spawnPlayer(this.characterId);
		// Apply difficulty HP bonus on top of base HP
		if (mod.playerHpBonus > 0) {
			this.player.applyHpBonus(mod.playerHpBonus);
		}

		// Player vs enemies (damage)
		this.physics.add.overlap(this.player, this.enemies, (_p, eObj) => {
			const e = eObj as Enemy;
			if (!e.active) return;
			if (e.kind === 'leash') {
				this.player.takeDamage(1);
				return;
			}
			this.player.takeDamage(e.contactDamage);
			if (e.kind === 'peloton') e.takeHit(99);
		});

		this.physics.add.overlap(this.player, this.coffees, (_p, c) => {
			(c as Coffee).onPlayerOverlap();
		});

		// Projectiles vs enemies
		this.physics.add.overlap(this.projectiles, this.enemies, (proj, enemyObj) => {
			const p = proj as Projectile;
			const e = enemyObj as Enemy;
			if (!e.active) return;
			if (p.tryHit(e)) {
				e.takeHit(p.damage);
			}
		});

		this.level.start();
		this.prevTime = this.time.now;

		const offResume = bridge.on('resumeFromDialogue', () => this.scene.resume());
		const offRequestPause = bridge.on('requestPause', () => this.scene.pause());
		const offRequestResume = bridge.on('requestResume', () => this.scene.resume());
		this.cleanupHandlers.push(offResume, offRequestPause, offRequestResume);

		const offDialogue = bridge.on('dialogue', (line) => {
			if (line) this.scene.pause();
		});
		this.cleanupHandlers.push(offDialogue);

		this.events.on(Phaser.Scenes.Events.RESUME, () => {
			this.prevTime = this.time.now;
		});

		this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
			for (const fn of this.cleanupHandlers) fn();
			this.cleanupHandlers = [];
			// Ensure Spine overlays don't outlive the scene
			for (const ref of [this.spineRosie, this.spineBoss]) {
				if (ref) {
					try { (ref as Phaser.GameObjects.GameObject).destroy(); } catch { /* ignored */ }
				}
			}
			this.spineRosie = undefined;
			this.spineBoss = undefined;
		});

		this.createSpinePlayer();
	}

	private spineRosie?: SpineCharacterObject;
	private spineBoss?: SpineCharacterObject;
	private playerShadow?: Phaser.GameObjects.Ellipse;
	private bossShadow?: Phaser.GameObjects.Ellipse;

	private createSpinePlayer() {
		const sceneAny = this as unknown as {
			add: { spine?: (x: number, y: number, dataKey: string, atlasKey: string, boundsProvider?: unknown) => unknown };
		};
		if (!sceneAny.add.spine) return;
		const id = this.characterId;
		// All characters at the same on-screen scale; per-character drawn
		// sizes vary slightly so this isn't perfectly uniform but reads as
		// the same visual presence.
		const SPINE_SCALE = 0.50;
		try {
			let bp: unknown = undefined;
			const spineModule = this.registry.get('spineModule') as
				| { SkinsAndAnimationBoundsProvider?: new (a: string | null) => unknown }
				| undefined;
			if (spineModule?.SkinsAndAnimationBoundsProvider) {
				bp = new spineModule.SkinsAndAnimationBoundsProvider(null);
			}
			// Soft drop shadow under the character — grounds them in the
			// scene the way Magic Design Studios games do.
			this.playerShadow = this.add
				.ellipse(this.player.x, this.player.y + 28, 56, 14, 0x0d1018, 0.45)
				.setDepth(199);

			const obj = sceneAny.add.spine(this.player.x, this.player.y, `${id}-data`, `${id}-atlas`, bp) as SpineCharacterObject;
			if (!obj) throw new Error('add.spine returned undefined');
			obj.setScale(SPINE_SCALE);
			obj.setDepth(200);
			obj.animationState?.setAnimation(0, 'idle', true);
			this.spineRosie = obj;
			(this.player as Phaser.GameObjects.Sprite).setAlpha(0);
		} catch (err) {
			console.error('[spine] create player failed:', err);
		}
	}

	private createSpineBoss() {
		if (!this.boss) return;
		const sceneAny = this as unknown as {
			add: { spine?: (x: number, y: number, dataKey: string, atlasKey: string, boundsProvider?: unknown) => unknown };
		};
		if (!sceneAny.add.spine) return;
		try {
			let bp: unknown = undefined;
			const spineModule = this.registry.get('spineModule') as
				| { SkinsAndAnimationBoundsProvider?: new (a: string | null) => unknown }
				| undefined;
			if (spineModule?.SkinsAndAnimationBoundsProvider) {
				bp = new spineModule.SkinsAndAnimationBoundsProvider(null);
			}
			// Drop shadow under the boss
			this.bossShadow = this.add
				.ellipse(this.boss.x, this.boss.y + 32, 80, 18, 0x0d1018, 0.45)
				.setDepth(6);

			const sb = sceneAny.add.spine(this.boss.x, this.boss.y, 'influencer-data', 'influencer-atlas', bp) as SpineCharacterObject;
			if (!sb) return;
			sb.setScale(0.45);
			sb.setDepth(7);
			sb.animationState?.setAnimation(0, 'idle', true);
			this.spineBoss = sb;
			// Hide the legacy boss sprite — Spine takes over rendering, but the
			// physics body / phone hitbox stay alive on the original GameObject.
			(this.boss as Phaser.GameObjects.Sprite).setAlpha(0);
		} catch (err) {
			console.error('[spine] boss create failed:', err);
		}
	}

	private spawnPlayer(id: CharacterId): Player {
		const x = GAME_WIDTH / 2;
		const y = GAME_HEIGHT - 110;
		switch (id) {
			case 'rosie':
				return new Rosie(this, x, y);
			case 'katie':
				return new Katie(this, x, y);
			case 'charlie':
				return new Charlie(this, x, y);
			case 'nancy':
				return new Nancy(this, x, y);
			case 'tia':
				return new Tia(this, x, y);
		}
	}

	update(time: number, _delta: number) {
		if (this.ended) return;
		const deltaMs = time - this.prevTime;
		this.prevTime = time;
		const deltaSec = deltaMs / 1000;
		const elapsedSec = this.level.getElapsed() / 1000;

		this.background.update(deltaSec, elapsedSec);
		this.scenery.update(deltaSec, this.background.currentSpeed());

		const input = this.input_.read();
		if (input.pausePressed) {
			bridge.emit('requestPause', undefined);
			return;
		}
		this.player.tickMovement(input.dx, input.dy);
		if (input.attackPressed) this.player.tryAttack(time);
		if (input.specialPressed) this.player.trySpecial(time);
		this.player.emitSpecialReady();

		const scrollSpeed = this.background.currentSpeed();
		for (const obj of this.enemies.getChildren()) {
			const e = obj as Enemy;
			if (!e.active) continue;
			e.tick(deltaSec, scrollSpeed);
			if (e.y > GAME_HEIGHT + 40) e.destroy();
		}
		for (const obj of this.coffees.getChildren()) {
			const c = obj as Coffee;
			if (!c.active) continue;
			c.tick(deltaSec, scrollSpeed);
			if (c.y > GAME_HEIGHT + 40) c.destroy();
		}

		this.level.tick(deltaMs, scrollSpeed);
		this.combo.tick();

		if (this.boss) this.boss.tick(deltaSec, scrollSpeed);

		const r = this.spineRosie;
		if (r && this.player.active) {
			r.setPosition(this.player.x, this.player.y);
			const vx = this.player.body?.velocity.x ?? 0;
			const vy = this.player.body?.velocity.y ?? 0;
			const desired = Math.abs(vx) > 1 || Math.abs(vy) > 1 ? 'walk' : 'idle';
			const current = r.animationState?.tracks?.[0]?.animation?.name;
			if (current !== desired) r.animationState?.setAnimation(0, desired, true);
		}
		if (this.playerShadow && this.player.active) {
			this.playerShadow.setPosition(this.player.x, this.player.y + 28);
		}

		const sb = this.spineBoss;
		if (sb && this.boss && this.boss.active) {
			sb.setPosition(this.boss.x, this.boss.y);
		}
		if (this.bossShadow && this.boss && this.boss.active) {
			this.bossShadow.setPosition(this.boss.x, this.boss.y + 32);
		}
	}

	spawnBoss() {
		const mod = DIFFICULTIES[this.difficulty];
		this.boss = new MainCharacterBoss(this, mod.bossHpMult);
		this.bossPhoneRing = this.add
			.circle(this.boss.phoneX(), this.boss.phoneY(), 22, 0xff3333, 0)
			.setStrokeStyle(2, 0xff3333, 0.8)
			.setDepth(9);

		// Spine overlay for the boss
		if (this.boss) this.createSpineBoss();

		this.physics.add.overlap(this.player, this.boss, () => this.player.takeDamage(1));
		// Projectiles damage the boss's phone hitbox
		this.physics.add.overlap(this.projectiles, this.boss, (proj, b) => {
			const p = proj as Projectile;
			const boss = b as MainCharacterBoss;
			if (!boss.active) return;
			// Only count hits that are within the phone's small hitbox
			const dx = p.x - boss.phoneX();
			const dy = p.y - boss.phoneY();
			if (Math.hypot(dx, dy) < 32) {
				if (p.tryHit(boss as unknown as Enemy)) boss.hitPhone(p.damage);
			}
		});
	}

	spawnFollower(x: number, y: number) {
		const p = new Peloton(this, x, y, this.background.currentSpeed());
		this.enemies.add(p);
	}

	onBossDefeated() {
		if (this.ended) return;
		this.endRun(true);
	}

	endRun(victory: boolean) {
		if (this.ended) return;
		this.ended = true;
		const distance = Math.floor(this.level.getElapsed() / 100);
		this.saveHighScore(distance);
		bridge.emit('gameOver', { distance, character: this.characterId, victory });
		this.scene.pause();
	}

	private saveHighScore(distance: number) {
		try {
			const raw = localStorage.getItem(STORAGE_KEYS.highScores);
			const data: Record<string, Record<string, number>> = raw ? JSON.parse(raw) : {};
			const lvl = (data[katyTrail.id] = data[katyTrail.id] || {});
			if (!lvl[this.characterId] || distance > lvl[this.characterId]) {
				lvl[this.characterId] = distance;
			}
			localStorage.setItem(STORAGE_KEYS.highScores, JSON.stringify(data));
		} catch {
			/* non-fatal */
		}
	}
}
