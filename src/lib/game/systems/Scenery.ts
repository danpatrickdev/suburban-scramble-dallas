import Phaser from 'phaser';
import type { GameScene } from '../scenes/GameScene';
import { GAME_HEIGHT, GAME_WIDTH } from '../constants';

// Drops decorative props on either grass strip as the world scrolls.
// Uptown / Katy Trail vibe: high-rise apartments, restaurants with awnings,
// brick mailboxes, construction cranes, lamp posts, benches, trees, signs,
// distant joggers. No collisions — purely visual flair.

interface SceneryProp {
	gfx: Phaser.GameObjects.Graphics;
	speedMult: number;
}

type Side = 'left' | 'right';

export class Scenery {
	private scene: GameScene;
	private props: SceneryProp[] = [];
	private spawnTimer = 0;
	private nextSide: Side = 'left';

	constructor(scene: GameScene) {
		this.scene = scene;
	}

	update(deltaSec: number, scrollSpeed: number) {
		this.spawnTimer += deltaSec;
		// Spawn frequently so the screen always has something
		if (this.spawnTimer > 0.42) {
			this.spawnTimer = 0;
			this.spawnRandom();
		}
		for (let i = this.props.length - 1; i >= 0; i--) {
			const p = this.props[i];
			p.gfx.y += scrollSpeed * p.speedMult * deltaSec;
			if (p.gfx.y > GAME_HEIGHT + 200) {
				p.gfx.destroy();
				this.props.splice(i, 1);
			}
		}
	}

	private spawnRandom() {
		const r = Math.random();
		if (r < 0.16) this.spawnHighRise();
		else if (r < 0.28) this.spawnRestaurant();
		else if (r < 0.40) this.spawnBrickMailbox();
		else if (r < 0.50) this.spawnConstructionCrane();
		else if (r < 0.60) this.spawnTree();
		else if (r < 0.70) this.spawnLampPost();
		else if (r < 0.78) this.spawnBench();
		else if (r < 0.86) this.spawnFirePit();
		else if (r < 0.95) this.spawnJoggerSilhouette();
		else this.spawnSign();
	}

	private nextSidePick(): Side {
		const s = this.nextSide;
		this.nextSide = s === 'left' ? 'right' : 'left';
		return s;
	}

	// Returns x for a small prop placed on the grass strip
	private grassEdgeX(width = 14, side?: Side): number {
		const margin = 6;
		const sideChoice = side ?? this.nextSidePick();
		if (sideChoice === 'left') {
			return Phaser.Math.Between(margin, 85 - width);
		}
		return Phaser.Math.Between(GAME_WIDTH - 85, GAME_WIDTH - margin - width);
	}

	// Returns x for a large prop that anchors to the outer edge of the screen
	private outerEdgeX(width: number, side?: Side): number {
		const sideChoice = side ?? this.nextSidePick();
		return sideChoice === 'left' ? 0 : GAME_WIDTH - width;
	}

	private spawnHighRise() {
		const g = this.scene.add.graphics();
		const w = Phaser.Math.Between(48, 76);
		const h = Phaser.Math.Between(160, 240);
		const side = this.nextSidePick();
		const x = side === 'left' ? 0 : GAME_WIDTH - w;
		// Building body
		g.fillStyle(0x46506a, 1);
		g.fillRect(x, 0, w, h);
		// Edge highlight
		g.fillStyle(0x5a667e, 1);
		g.fillRect(side === 'left' ? x + w - 2 : x, 0, 2, h);
		// Windows grid
		const colColor = [0xffd180, 0xfff5a8, 0x88e1ff, 0x14182a];
		for (let row = 6; row < h - 8; row += 8) {
			for (let col = 4; col < w - 4; col += 6) {
				const lit = (row * 13 + col * 7 + Math.floor(this.scene.time.now / 500)) % 4;
				g.fillStyle(colColor[lit] ?? 0x14182a, 1);
				g.fillRect(x + col, row, 3, 4);
			}
		}
		// Rooftop
		g.fillStyle(0x32384a, 1);
		g.fillRect(x, 0, w, 5);
		g.fillRect(x + w / 2 - 4, -8, 8, 8);
		g.setPosition(0, -h - 10);
		g.setDepth(-3);
		this.props.push({ gfx: g, speedMult: 0.85 });
	}

	private spawnRestaurant() {
		const g = this.scene.add.graphics();
		const w = 56;
		const h = 44;
		const side = this.nextSidePick();
		const x = side === 'left' ? 4 : GAME_WIDTH - w - 4;
		// Building base (brick)
		g.fillStyle(0x9c4a3c, 1);
		g.fillRect(x, 8, w, h);
		// Mortar lines
		for (let row = 12; row < h + 6; row += 6) {
			g.fillStyle(0x7a3a30, 1);
			g.fillRect(x, row, w, 1);
		}
		// Awning (striped pink/white)
		const stripes = 7;
		for (let s = 0; s < stripes; s++) {
			g.fillStyle(s % 2 === 0 ? 0xf8b6cb : 0xffffff, 1);
			g.fillRect(x + (w / stripes) * s, 0, w / stripes, 8);
		}
		// Awning trim
		g.fillStyle(0xd084a4, 1);
		g.fillRect(x, 8, w, 1);
		// Door
		g.fillStyle(0x32384a, 1);
		g.fillRect(x + w / 2 - 4, h - 10, 8, 18);
		g.fillStyle(0xffd500, 1);
		g.fillRect(x + w / 2 + 1, h - 4, 1, 1);
		// Windows
		g.fillStyle(0xffd180, 1);
		g.fillRect(x + 6, 16, 8, 10);
		g.fillRect(x + w - 14, 16, 8, 10);
		// Sign on top
		g.fillStyle(0xfff5a8, 1);
		g.fillRect(x + 8, -6, w - 16, 6);
		g.fillStyle(0x14182a, 1);
		g.fillRect(x + 12, -3, w - 24, 1);
		g.setPosition(0, -h - 20);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	private spawnBrickMailbox() {
		const g = this.scene.add.graphics();
		const x = this.grassEdgeX(14);
		// Brick column
		g.fillStyle(0x9c4a3c, 1);
		g.fillRect(x, 4, 12, 18);
		for (let r = 7; r < 22; r += 5) {
			g.fillStyle(0x7a3a30, 1);
			g.fillRect(x, r, 12, 1);
		}
		// Mailbox on top
		g.fillStyle(0x32384a, 1);
		g.fillRect(x - 1, 0, 14, 6);
		// Flag
		g.fillStyle(0xff3b5c, 1);
		g.fillRect(x + 13, 1, 3, 4);
		g.setPosition(0, -25);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	private spawnConstructionCrane() {
		const g = this.scene.add.graphics();
		const w = 90;
		const h = 220;
		const side = this.nextSidePick();
		const x = side === 'left' ? 0 : GAME_WIDTH - w;
		// Vertical mast (yellow construction)
		g.fillStyle(0xffb000, 1);
		g.fillRect(x + (side === 'left' ? 8 : w - 12), 20, 4, h - 20);
		// Lattice X marks
		for (let yy = 30; yy < h - 10; yy += 14) {
			g.lineStyle(1, 0xc88800, 1);
			g.strokeLineShape(new Phaser.Geom.Line(x + (side === 'left' ? 8 : w - 12), yy, x + (side === 'left' ? 12 : w - 8), yy + 7));
			g.strokeLineShape(new Phaser.Geom.Line(x + (side === 'left' ? 12 : w - 8), yy, x + (side === 'left' ? 8 : w - 12), yy + 7));
		}
		// Horizontal arm
		g.fillStyle(0xffb000, 1);
		g.fillRect(x + (side === 'left' ? 0 : w - 80), 14, 80, 4);
		// Counter-jib
		g.fillRect(x + (side === 'left' ? 0 : w - 24), 10, 24, 8);
		// Cab
		g.fillStyle(0x32384a, 1);
		g.fillRect(x + (side === 'left' ? 6 : w - 14), 8, 8, 8);
		// Hook hanging
		g.fillStyle(0x666870, 1);
		g.fillRect(x + (side === 'left' ? 60 : w - 64), 18, 1, 22);
		g.fillStyle(0xff3b5c, 1);
		g.fillRect(x + (side === 'left' ? 58 : w - 66), 40, 5, 4);
		g.setPosition(0, -h - 10);
		g.setDepth(-3);
		this.props.push({ gfx: g, speedMult: 0.92 });
	}

	private spawnFirePit() {
		const g = this.scene.add.graphics();
		const x = this.grassEdgeX(20);
		// Stone ring
		g.fillStyle(0x7a7a82, 1);
		g.fillEllipse(x + 10, 10, 18, 6);
		g.fillStyle(0x5a5a62, 1);
		g.fillEllipse(x + 10, 12, 18, 4);
		// Fire (pink/orange suburban-luxe vibes)
		g.fillStyle(0xff6a3c, 1);
		g.fillEllipse(x + 10, 6, 10, 6);
		g.fillStyle(0xffd500, 1);
		g.fillEllipse(x + 10, 5, 6, 4);
		g.fillStyle(0xfff5a8, 0.9);
		g.fillEllipse(x + 10, 4, 3, 2);
		g.setPosition(0, -20);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	private spawnLampPost() {
		const g = this.scene.add.graphics();
		const x = this.grassEdgeX(8);
		g.fillStyle(0x2a2a30, 1);
		g.fillRect(x, 0, 3, 32);
		g.fillStyle(0x4a4a50, 1);
		g.fillRect(x - 4, 0, 11, 4);
		g.fillStyle(0xfff5a8, 0.5);
		g.fillCircle(x + 1, 4, 7);
		g.fillStyle(0xffd500, 0.9);
		g.fillCircle(x + 1, 4, 2);
		g.setPosition(0, -45);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	private spawnBench() {
		const g = this.scene.add.graphics();
		const x = this.grassEdgeX(28);
		g.fillStyle(0x6a4a2a, 1);
		g.fillRect(x, 0, 26, 3);
		g.fillRect(x, 5, 26, 3);
		g.fillStyle(0x3a2a1a, 1);
		g.fillRect(x + 1, 0, 2, 13);
		g.fillRect(x + 23, 0, 2, 13);
		g.setPosition(0, -30);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	private spawnTree() {
		const g = this.scene.add.graphics();
		const x = this.grassEdgeX(18);
		g.fillStyle(0x3a2a1a, 1);
		g.fillRect(x + 6, 14, 5, 14);
		g.fillStyle(0x1f5a1f, 1);
		g.fillCircle(x + 9, 10, 13);
		g.fillStyle(0x2f7a2f, 1);
		g.fillCircle(x + 5, 7, 9);
		g.fillStyle(0x4f9a4f, 1);
		g.fillCircle(x + 13, 6, 7);
		g.setPosition(0, -45);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	private spawnJoggerSilhouette() {
		const g = this.scene.add.graphics();
		const x = Phaser.Math.Between(90, GAME_WIDTH - 90);
		const colors = [0xff3b5c, 0x88e1ff, 0xfff5a8, 0xb8a3ff, 0x70d0a0];
		const c = colors[Math.floor(Math.random() * colors.length)];
		g.fillStyle(c, 0.9);
		g.fillRect(x, 5, 5, 7);
		g.fillStyle(0xeac5a4, 1);
		g.fillCircle(x + 2, 2, 2);
		g.fillStyle(0x222226, 1);
		g.fillRect(x, 12, 2, 5);
		g.fillRect(x + 3, 12, 2, 5);
		g.setPosition(0, -22);
		g.setDepth(-1);
		this.props.push({ gfx: g, speedMult: 1.18 });
	}

	private spawnSign() {
		const g = this.scene.add.graphics();
		const x = this.grassEdgeX(16);
		g.fillStyle(0x2a2a30, 1);
		g.fillRect(x + 6, 10, 2, 14);
		g.fillStyle(0xf8b6cb, 1);
		g.fillRect(x, 0, 16, 10);
		g.lineStyle(1, 0x14182a, 1);
		g.strokeRect(x, 0, 16, 10);
		g.fillStyle(0x14182a, 1);
		g.fillRect(x + 2, 2, 12, 1);
		g.fillRect(x + 2, 4, 10, 1);
		g.fillRect(x + 2, 6, 8, 1);
		g.setPosition(0, -30);
		g.setDepth(-2);
		this.props.push({ gfx: g, speedMult: 1 });
	}

	destroy() {
		for (const p of this.props) p.gfx.destroy();
		this.props = [];
	}
}
