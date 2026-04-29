import type { LevelDef, DialogueTrigger, CharacterId, WaveDef } from '../types';
import type { GameScene } from '../scenes/GameScene';
import type { DifficultyMod } from '../data/difficulty';
import { bridge } from '../PhaserBridge';

export class LevelManager {
	private scene: GameScene;
	private level: LevelDef;
	private character: CharacterId;
	private mod: DifficultyMod;
	private elapsed = 0;
	private waveIdx = 0;
	private waves: WaveDef[];
	private dialogueDone = new Set<DialogueTrigger>();
	private bossSpawned = false;
	private filler = 0;

	constructor(scene: GameScene, level: LevelDef, character: CharacterId, mod: DifficultyMod) {
		this.scene = scene;
		this.level = level;
		this.character = character;
		this.mod = mod;
		this.waves = this.buildWaves();
	}

	private buildWaves(): WaveDef[] {
		const { waveFrequencyMult, enemyCountMult } = this.mod;
		// Multiply enemy counts and interpolate extra waves between existing ones
		// to honor waveFrequencyMult.
		const base = this.level.waves;
		const out: WaveDef[] = base.map((w) => ({
			...w,
			count: Math.max(1, Math.round(w.count * enemyCountMult))
		}));

		if (waveFrequencyMult > 1) {
			// Insert "filler" waves between consecutive original waves to raise spawn rate
			const extras: WaveDef[] = [];
			const extraPerGap = Math.floor(waveFrequencyMult) - 1 + (waveFrequencyMult % 1 > 0 ? 1 : 0);
			for (let i = 0; i < base.length - 1; i++) {
				const a = base[i];
				const b = base[i + 1];
				for (let k = 1; k <= extraPerGap; k++) {
					const t = a.at + ((b.at - a.at) * k) / (extraPerGap + 1);
					// Pick the kind randomly between adjacent waves; favor pelotons
					const r = Math.random();
					const kind: WaveDef['kind'] = r < 0.7 ? 'peloton' : r < 0.9 ? 'coffee' : 'leash';
					const count = Math.max(1, Math.round((kind === 'leash' ? 1 : 2) * enemyCountMult));
					extras.push({ at: t, kind, count, pattern: 'spread' });
				}
			}
			out.push(...extras);
			out.sort((a, b) => a.at - b.at);
		}

		return out;
	}

	start() {
		for (const trig of this.level.dialogue) {
			if (trig.at !== -1) continue;
			if (trig.character && trig.character !== this.character) continue;
			this.fire(trig);
			break;
		}
	}

	tick(deltaMs: number, scrollSpeed: number) {
		if (this.scene.scene.isPaused()) return;
		this.elapsed += deltaMs;

		while (this.waveIdx < this.waves.length && this.waves[this.waveIdx].at <= this.elapsed) {
			const wave = this.waves[this.waveIdx++];
			this.scene.factory.spawnWave(wave, scrollSpeed);
		}

		// On hard / x_games, also drip-spawn small filler enemies between waves
		// so the screen never feels empty.
		this.filler += deltaMs;
		const fillerInterval = this.mod.waveFrequencyMult >= 2 ? 600
			: this.mod.waveFrequencyMult >= 1.4 ? 1100
			: 99_999;
		if (this.filler >= fillerInterval && !this.bossSpawned) {
			this.filler = 0;
			this.scene.factory.spawnOne('peloton', Math.random() * (this.scene.game.config.width as number - 60) + 30, -40, scrollSpeed);
		}

		for (const trig of this.level.dialogue) {
			if (trig.at < 0) continue;
			if (trig.at > this.elapsed) continue;
			if (this.dialogueDone.has(trig)) continue;
			if (trig.character && trig.character !== this.character) {
				this.dialogueDone.add(trig);
				continue;
			}
			this.fire(trig);
			break;
		}

		if (!this.bossSpawned && this.elapsed >= this.level.durationMs) {
			this.bossSpawned = true;
			this.scene.spawnBoss();
			for (const trig of this.level.dialogue) {
				if (trig.at !== -2) continue;
				this.fire(trig);
				break;
			}
		}

		bridge.emit('distanceChange', { distance: Math.floor(this.elapsed / 100) });
	}

	private fire(trig: DialogueTrigger) {
		this.dialogueDone.add(trig);
		bridge.emit('dialogue', trig.line);
	}

	getElapsed(): number {
		return this.elapsed;
	}
}
