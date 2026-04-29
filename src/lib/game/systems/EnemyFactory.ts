import Phaser from 'phaser';
import type { GameScene } from '../scenes/GameScene';
import type { WaveDef } from '../types';
import { GAME_WIDTH } from '../constants';
import { Peloton } from '../entities/enemies/Peloton';
import { Leash } from '../entities/enemies/Leash';
import { Coffee } from '../entities/enemies/Coffee';
import type { Enemy } from '../entities/Enemy';

export class EnemyFactory {
	private scene: GameScene;
	constructor(scene: GameScene) {
		this.scene = scene;
	}

	spawnWave(wave: WaveDef, scrollSpeed: number) {
		const enemies: Enemy[] = [];
		const xs = this.computePattern(wave.count, wave.pattern);
		for (const x of xs) {
			const e = this.spawnOne(wave.kind, x, -40, scrollSpeed);
			if (e) enemies.push(e);
		}
		return enemies;
	}

	spawnOne(kind: WaveDef['kind'], x: number, y: number, scrollSpeed: number): Enemy | null {
		switch (kind) {
			case 'peloton':
				return this.scene.enemies.add(new Peloton(this.scene, x, y, scrollSpeed)) as unknown as Enemy;
			case 'leash':
				return this.scene.enemies.add(new Leash(this.scene, x, y)) as unknown as Enemy;
			case 'coffee': {
				const coffee = new Coffee(this.scene, x, y);
				this.scene.coffees.add(coffee);
				return coffee as unknown as Enemy;
			}
			default:
				return null;
		}
	}

	private computePattern(count: number, pattern: WaveDef['pattern']): number[] {
		const margin = 32;
		const usable = GAME_WIDTH - margin * 2;
		const xs: number[] = [];
		switch (pattern) {
			case 'line': {
				// All in one column
				const x = Phaser.Math.Between(margin, GAME_WIDTH - margin);
				for (let i = 0; i < count; i++) xs.push(x);
				break;
			}
			case 'spread': {
				for (let i = 0; i < count; i++) {
					const x = margin + (usable * (i + 0.5)) / count;
					xs.push(x);
				}
				break;
			}
			case 'random':
			default: {
				for (let i = 0; i < count; i++) xs.push(Phaser.Math.Between(margin, GAME_WIDTH - margin));
			}
		}
		return xs;
	}
}
