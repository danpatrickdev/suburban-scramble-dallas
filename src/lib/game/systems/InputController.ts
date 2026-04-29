import Phaser from 'phaser';

export interface InputState {
	dx: number; // -1, 0, 1
	dy: number;
	attackPressed: boolean;
	specialPressed: boolean;
	pausePressed: boolean;
}

export class InputController {
	private scene: Phaser.Scene;
	private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
	private wasd!: { W: Phaser.Input.Keyboard.Key; A: Phaser.Input.Keyboard.Key; S: Phaser.Input.Keyboard.Key; D: Phaser.Input.Keyboard.Key };
	private space!: Phaser.Input.Keyboard.Key;
	private shift!: Phaser.Input.Keyboard.Key;
	private esc!: Phaser.Input.Keyboard.Key;
	private locked = false;
	private slipUntil = 0;

	constructor(scene: Phaser.Scene) {
		this.scene = scene;
		const kb = scene.input.keyboard!;
		this.cursors = kb.createCursorKeys();
		this.wasd = {
			W: kb.addKey(Phaser.Input.Keyboard.KeyCodes.W),
			A: kb.addKey(Phaser.Input.Keyboard.KeyCodes.A),
			S: kb.addKey(Phaser.Input.Keyboard.KeyCodes.S),
			D: kb.addKey(Phaser.Input.Keyboard.KeyCodes.D)
		};
		this.space = kb.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
		this.shift = kb.addKey(Phaser.Input.Keyboard.KeyCodes.SHIFT);
		this.esc = kb.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
	}

	setLocked(locked: boolean) {
		this.locked = locked;
	}

	slipFor(ms: number) {
		this.slipUntil = Math.max(this.slipUntil, this.scene.time.now + ms);
	}

	read(): InputState {
		if (this.locked) {
			return { dx: 0, dy: 0, attackPressed: false, specialPressed: false, pausePressed: false };
		}
		const slipping = this.scene.time.now < this.slipUntil;
		const left = (this.cursors.left.isDown || this.wasd.A.isDown) ? 1 : 0;
		const right = (this.cursors.right.isDown || this.wasd.D.isDown) ? 1 : 0;
		const up = (this.cursors.up.isDown || this.wasd.W.isDown) ? 1 : 0;
		const down = (this.cursors.down.isDown || this.wasd.S.isDown) ? 1 : 0;

		let dx = right - left;
		let dy = down - up;

		if (slipping) {
			// Invert horizontal & dampen vertical to simulate slipping
			dx = -dx * 0.5;
			dy = dy * 0.3 + 0.4; // pulled forward slightly
		}

		return {
			dx,
			dy,
			attackPressed: Phaser.Input.Keyboard.JustDown(this.space),
			specialPressed: Phaser.Input.Keyboard.JustDown(this.shift),
			pausePressed: Phaser.Input.Keyboard.JustDown(this.esc)
		};
	}
}
