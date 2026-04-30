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
			// Ensure the Spine overlay doesn't outlive the scene
			if (this.spineRosie) {
				try {
					(this.spineRosie as Phaser.GameObjects.GameObject).destroy();
				} catch {
					// already destroyed
				}
				this.spineRosie = undefined;
			}
		});

		if (this.registry.get('spineTest')) {
			this.renderSpineTest();
		}
	}

	private spineRosie?: SpineCharacterObject;

	private renderSpineTest() {
		console.log('[spineTest] starting');
		const sceneAny = this as unknown as {
			add: { spine?: (x: number, y: number, dataKey: string, atlasKey: string) => unknown };
			spine?: unknown;
		};
		console.log('[spineTest] add.spine type:', typeof sceneAny.add.spine, '| this.spine:', !!sceneAny.spine);

		const banner = this.add.text(8, 8, '[SPINE] booting...', {
			fontFamily: 'monospace',
			fontSize: '11px',
			color: '#88e1ff',
			backgroundColor: '#0c0e14'
		}).setDepth(1000);

		if (!sceneAny.add.spine) {
			banner.setText('[SPINE] FAIL — add.spine not available (plugin not registered)').setColor('#ff3b5c');
			return;
		}

		this.createSpineRosie(banner);
	}

	private createSpineRosie(banner?: Phaser.GameObjects.Text) {
		const sceneAny = this as unknown as {
			add: { spine?: (x: number, y: number, dataKey: string, atlasKey: string, boundsProvider?: unknown) => unknown };
		};
		if (!sceneAny.add.spine) {
			banner?.setText('[SPINE] FAIL — add.spine not available').setColor('#ff3b5c');
			return;
		}
		try {
			// Use SkinsAndAnimationBoundsProvider so bones that extend during animation
			// are accounted for. Pulled from the registry (PhaserGame.ts stores the
			// module after dynamic import).
			let bp: unknown = undefined;
			const spineModule = this.registry.get('spineModule') as
				| { SkinsAndAnimationBoundsProvider?: new (a: string | null) => unknown }
				| undefined;
			if (spineModule?.SkinsAndAnimationBoundsProvider) {
				bp = new spineModule.SkinsAndAnimationBoundsProvider(null);
			}
			const rosie = sceneAny.add.spine(this.player.x, this.player.y, 'rosie-data', 'rosie-atlas', bp) as SpineCharacterObject;
			if (!rosie) throw new Error('add.spine returned undefined');
			rosie.setScale(0.35);
			rosie.setDepth(200);
			rosie.animationState?.setAnimation(0, 'idle', true);
			this.spineRosie = rosie;
			(this.player as Phaser.GameObjects.Sprite).setAlpha(0);
			banner?.setText('[SPINE] OK — Rosie rigged');
		} catch (err) {
			banner?.setText('[SPINE] FAIL — ' + (err as Error).message).setColor('#ff3b5c');
			console.error('[spineTest] create failed:', err);
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
	}

	spawnBoss() {
		const mod = DIFFICULTIES[this.difficulty];
		this.boss = new MainCharacterBoss(this, mod.bossHpMult);
		this.bossPhoneRing = this.add
			.circle(this.boss.phoneX(), this.boss.phoneY(), 22, 0xff3333, 0)
			.setStrokeStyle(2, 0xff3333, 0.8)
			.setDepth(9);

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
