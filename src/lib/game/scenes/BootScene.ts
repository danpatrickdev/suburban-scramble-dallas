import Phaser from 'phaser';
import { CHARACTER_IDS } from '../data/characters';
import { katyTrail } from '../data/levels/katyTrail';
import { GAME_HEIGHT, GAME_WIDTH } from '../constants';

export class BootScene extends Phaser.Scene {
	constructor() {
		super('Boot');
	}

	preload() {
		// Loading bar
		const w = GAME_WIDTH * 0.6;
		const h = 6;
		const x = (GAME_WIDTH - w) / 2;
		const y = GAME_HEIGHT / 2 + 30;
		const border = this.add.rectangle(x, y, w, h, 0xffffff, 0).setOrigin(0, 0.5);
		border.setStrokeStyle(1, 0xffffff);
		const fill = this.add.rectangle(x, y, 0, h - 2, 0xf8b6cb).setOrigin(0, 0.5);
		this.add
			.text(GAME_WIDTH / 2, GAME_HEIGHT / 2 - 10, 'SUBURBAN\nSCRAMBLE', {
				fontFamily: 'monospace',
				fontSize: '20px',
				color: '#f8b6cb',
				align: 'center'
			})
			.setOrigin(0.5);
		this.add
			.text(GAME_WIDTH / 2, y + 18, 'loading...', {
				fontFamily: 'monospace',
				fontSize: '10px',
				color: '#888'
			})
			.setOrigin(0.5);

		this.load.on('progress', (p: number) => {
			fill.width = (w - 2) * p;
		});

		// Character atlases
		for (const id of CHARACTER_IDS) {
			this.load.atlas(
				`char_${id}`,
				`assets/characters/${id}.png`,
				`assets/characters/${id}.json`
			);
		}

		// Enemy atlases
		this.load.atlas('enemy_peloton', 'assets/enemies/peloton.png', 'assets/enemies/peloton.json');
		this.load.atlas('enemy_leash', 'assets/enemies/leash.png', 'assets/enemies/leash.json');
		this.load.atlas('enemy_coffee', 'assets/enemies/coffee.png', 'assets/enemies/coffee.json');

		// Boss
		this.load.atlas(
			'boss_main_character',
			'assets/bosses/main_character.png',
			'assets/bosses/main_character.json'
		);

		// Tiles
		this.load.image(katyTrail.tileKey, katyTrail.tilePath);

		// Optional Spine test asset — loaded only when the SpinePlugin is registered
		// (PhaserGame.ts toggles via ?spine URL flag).
		if (this.registry.get('spineTest')) {
			// `spine.SpinePlugin` exposes loader methods on `this.load.spine*`.
			const loader = this.load as Phaser.Loader.LoaderPlugin & {
				spineJson?: (key: string, url: string) => void;
				spineAtlas?: (key: string, url: string) => void;
			};
			// Rosie — our actual character, rigged via the Genielabs pipeline
			loader.spineJson?.('rosie-data', 'assets/spine/rosie/built/rosie.json');
			loader.spineAtlas?.('rosie-atlas', 'assets/spine/rosie/built/rosie.atlas');
		}
	}

	create() {
		// Build animations from atlas frame tags so Player code can just play('walk') etc.
		const animSets: Array<[string, number]> = [
			['idle', 8],
			['walk', 10],
			['attack', 18],
			['special', 14]
		];

		const buildAnims = (key: string) => {
			for (const [animName, frameRate] of animSets) {
				const frames: Phaser.Types.Animations.AnimationFrame[] = [];
				let i = 0;
				while (this.textures.get(key).has(`${animName}_${i}`)) {
					frames.push({ key, frame: `${animName}_${i}` });
					i++;
				}
				if (frames.length === 0) continue;
				const animKey = `${key}__${animName}`;
				if (this.anims.exists(animKey)) continue;
				this.anims.create({
					key: animKey,
					frames,
					frameRate,
					repeat: animName === 'idle' || animName === 'walk' ? -1 : 0
				});
			}
		};

		for (const id of CHARACTER_IDS) buildAnims(`char_${id}`);
		buildAnims('enemy_peloton');
		buildAnims('enemy_leash');
		buildAnims('enemy_coffee');
		buildAnims('boss_main_character');

		this.scene.start('Game');
	}
}
