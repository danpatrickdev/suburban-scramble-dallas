import { FRENZY_DURATION, FRENZY_KILLS_REQUIRED } from '../constants';
import { bridge } from '../PhaserBridge';
import type { GameScene } from '../scenes/GameScene';

export class ComboSystem {
	private scene: GameScene;
	combo = 0;
	frenzy = false;
	private frenzyUntil = 0;

	constructor(scene: GameScene) {
		this.scene = scene;
	}

	onKill() {
		this.combo += 1;
		if (!this.frenzy && this.combo >= FRENZY_KILLS_REQUIRED) {
			this.activateFrenzy();
		}
		bridge.emit('comboChange', { combo: this.combo, frenzy: this.frenzy });
	}

	onHit() {
		// Damage breaks the combo
		if (!this.frenzy) {
			this.combo = 0;
			bridge.emit('comboChange', { combo: 0, frenzy: false });
		}
	}

	private activateFrenzy() {
		this.frenzy = true;
		this.frenzyUntil = this.scene.time.now + FRENZY_DURATION;
		this.scene.player?.setFrenzy(true);
		this.scene.cameras.main.flash(200, 255, 255, 200);
	}

	tick() {
		if (this.frenzy && this.scene.time.now >= this.frenzyUntil) {
			this.frenzy = false;
			this.combo = 0;
			this.scene.player?.setFrenzy(false);
			bridge.emit('comboChange', { combo: 0, frenzy: false });
		}
	}
}
