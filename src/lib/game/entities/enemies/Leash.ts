import Phaser from 'phaser';
import { Enemy } from '../Enemy';
import type { GameScene } from '../../scenes/GameScene';
import { GAME_WIDTH } from '../../constants';

export class Leash extends Enemy {
	constructor(scene: GameScene, _x: number, y: number) {
		super(scene, GAME_WIDTH / 2, y, 'enemy_leash', 'leash', 4, 1);
		// Stretch horizontally to span the path; keep a thicker visual + hitbox.
		this.setDisplaySize(GAME_WIDTH, 22);
		this.body.setSize(GAME_WIDTH, 16).setOffset(0, 16);
		this.play('enemy_leash__walk');
	}

	tick(_deltaSec: number, scrollSpeed: number) {
		if (this.isStunned()) return;
		this.body.setVelocity(0, scrollSpeed);
	}
}
