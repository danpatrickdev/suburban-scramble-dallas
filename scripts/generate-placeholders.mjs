#!/usr/bin/env node
// Emits placeholder PNG sprite sheets + Phaser-compatible JSON atlases into static/assets/.
// Each character/enemy/boss gets a 4-row strip: idle (4), walk (4), attack (3), special (3).
// Frame size is configurable per asset. Output mirrors what an Aseprite "JSON Hash" export
// produces, so dropping in real Aseprite art later is a 1:1 file replacement.

import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const ASSETS = join(ROOT, 'static', 'assets');

const FRAME_SET = [
	{ name: 'idle', count: 4 },
	{ name: 'walk', count: 4 },
	{ name: 'attack', count: 3 },
	{ name: 'special', count: 3 }
];

const sprites = [
	// id, dir, size, palette { body, accent, highlight, eye, extra? }, style
	{ id: 'rosie',   dir: 'characters', size: 32, palette: { body: '#FFFFFF', accent: '#101010', highlight: '#FFB000', eye: '#FFB000' }, style: 'border_collie_classic' },
	{ id: 'charlie', dir: 'characters', size: 32, palette: { body: '#101010', accent: '#FFFFFF', highlight: '#7B4A1E', eye: '#7B4A1E' }, style: 'border_collie_tri' },
	{ id: 'katie',   dir: 'characters', size: 32, palette: { body: '#F8B6CB', accent: '#3A2B22', highlight: '#FFFFFF', eye: '#000000' }, style: 'human_athleisure' },
	{ id: 'tia',     dir: 'characters', size: 32, palette: { body: '#8C8F95', accent: '#FFFFFF', highlight: '#5A5C61', eye: '#3D8B3D' }, style: 'cat_large' },
	{ id: 'nancy',   dir: 'characters', size: 32, palette: { body: '#A6A8AC', accent: '#FFFFFF', highlight: '#5A5C61', eye: '#3D8B3D' }, style: 'cat_small' },

	{ id: 'peloton', dir: 'enemies', size: 32, palette: { body: '#101010', accent: '#FF1F4B', highlight: '#FFFFFF', eye: '#FFFFFF' }, style: 'cyclist' },
	{ id: 'leash',   dir: 'enemies', size: 48, palette: { body: '#3A3A3A', accent: '#D04848', highlight: '#FFFFFF', eye: '#000000' }, style: 'leash_line' },
	{ id: 'coffee',  dir: 'enemies', size: 32, palette: { body: '#5A3A1F', accent: '#FFFFFF', highlight: '#3A1F0A', eye: '#FFFFFF' }, style: 'coffee_splat' },

	{ id: 'main_character', dir: 'bosses', size: 64, palette: { body: '#F8B6CB', accent: '#000000', highlight: '#FFD500', eye: '#3A2B22' }, style: 'influencer' }
];

function hexToRgb(hex) {
	const m = hex.replace('#', '');
	return [parseInt(m.slice(0, 2), 16), parseInt(m.slice(2, 4), 16), parseInt(m.slice(4, 6), 16), 255];
}

function ensureDir(p) {
	if (!existsSync(p)) mkdirSync(p, { recursive: true });
}

// Draw a single frame into the png buffer at (offsetX, offsetY).
function drawFrame(png, offsetX, offsetY, size, palette, style, animName, frameIndex) {
	const set = (x, y, rgba) => {
		if (x < 0 || y < 0 || x >= size || y >= size) return;
		const idx = ((offsetY + y) * png.width + (offsetX + x)) * 4;
		png.data[idx] = rgba[0];
		png.data[idx + 1] = rgba[1];
		png.data[idx + 2] = rgba[2];
		png.data[idx + 3] = rgba[3];
	};
	const rect = (x, y, w, h, rgba) => {
		for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) set(x + xx, y + yy, rgba);
	};
	const circle = (cx, cy, r, rgba) => {
		for (let yy = -r; yy <= r; yy++)
			for (let xx = -r; xx <= r; xx++)
				if (xx * xx + yy * yy <= r * r) set(cx + xx, cy + yy, rgba);
	};

	const body = hexToRgb(palette.body);
	const accent = hexToRgb(palette.accent);
	const highlight = hexToRgb(palette.highlight);
	const eye = hexToRgb(palette.eye);

	// Cycle bob — different anims have different bob magnitudes
	const bobTable = { idle: [0, 0, 0, 0], walk: [0, -1, 0, 1], attack: [-1, 0, -1, 0], special: [-1, -2, -1, 0] };
	const bob = (bobTable[animName] || [0])[frameIndex] || 0;

	if (style === 'border_collie_classic' || style === 'border_collie_tri') {
		// Top-down dog: oval body, head with ears, tail
		const cx = size / 2;
		const cy = size / 2 + bob;
		// Body
		circle(cx, cy + 2, Math.floor(size / 4), accent); // saddle
		circle(cx, cy + 4, Math.floor(size / 5), body); // belly white
		// Head
		circle(cx, cy - 5, Math.floor(size / 5), accent);
		// White blaze
		rect(cx - 1, cy - 8, 2, 6, body);
		// Ears
		set(cx - 4, cy - 7, accent);
		set(cx + 3, cy - 7, accent);
		// Eyes
		set(cx - 2, cy - 5, eye);
		set(cx + 1, cy - 5, eye);
		// Tail (wagging on walk)
		const tailX = animName === 'walk' ? cx + 5 + (frameIndex % 2 === 0 ? 0 : 1) : cx + 5;
		set(tailX, cy + 5, accent);
		// Tri-color highlights for Charlie
		if (style === 'border_collie_tri') {
			set(cx - 3, cy - 6, highlight); // brow
			set(cx + 2, cy - 6, highlight); // brow
			rect(cx - 4, cy + 6, 2, 2, highlight); // tan leg
			rect(cx + 2, cy + 6, 2, 2, highlight);
		}
		// Attack frame: open mouth indicator
		if (animName === 'attack') circle(cx, cy - 8, 2, hexToRgb('#FF3030'));
		// Special frame: speed lines / glow
		if (animName === 'special') {
			rect(0, cy - 1, size, 1, highlight);
			rect(0, cy + 1, size, 1, highlight);
		}
	} else if (style === 'human_athleisure') {
		// Top-down human: head, ponytail, torso, arms
		const cx = size / 2;
		const cy = size / 2 + bob;
		// Body (pink top)
		rect(cx - 5, cy - 2, 10, 9, body);
		// Legs (black leggings)
		rect(cx - 4, cy + 6, 3, 6, accent);
		rect(cx + 1, cy + 6, 3, 6, accent);
		// Head
		circle(cx, cy - 6, 4, hexToRgb('#F2C9A0')); // skin tone
		// Brunette hair
		rect(cx - 4, cy - 10, 8, 3, accent);
		// Ponytail (longer in walk anim alternating)
		const ptLen = animName === 'walk' ? 4 + (frameIndex % 2) : 4;
		rect(cx - 1, cy - 7, 2, ptLen, accent);
		// Apple Watch (highlight on wrist)
		set(cx - 6, cy + 3, highlight);
		set(cx + 5, cy + 3, highlight);
		// Eyes
		set(cx - 1, cy - 6, eye);
		set(cx + 1, cy - 6, eye);
		// Attack: laser flash from watch
		if (animName === 'attack') {
			rect(cx + 5, cy + 2, 6 + frameIndex, 2, hexToRgb('#FF0000'));
		}
		// Special: bubble
		if (animName === 'special') {
			circle(cx, cy, 12, hexToRgb('#88E1FF80'));
		}
	} else if (style === 'cat_large' || style === 'cat_small') {
		// Top-down cat: rounder body, triangular ears
		const scale = style === 'cat_small' ? 0.85 : 1.0;
		const cx = size / 2;
		const cy = size / 2 + bob;
		const r = Math.floor((size / 4) * scale);
		// Body
		circle(cx, cy + 2, r, body);
		// White belly
		circle(cx, cy + 4, Math.floor(r * 0.6), accent);
		// Head
		circle(cx, cy - 4, Math.floor(r * 0.9), body);
		// Ears (triangles)
		set(cx - 4, cy - 9, body);
		set(cx - 5, cy - 8, body);
		set(cx + 3, cy - 9, body);
		set(cx + 4, cy - 8, body);
		// Eyes (green)
		set(cx - 2, cy - 4, eye);
		set(cx + 2, cy - 4, eye);
		// Tail
		const tailWag = animName === 'walk' ? frameIndex - 1 : 0;
		rect(cx + 5 + tailWag, cy + 1, 1, 5, body);
		// Tabby stripes (large cat only — confident look)
		if (style === 'cat_large') {
			set(cx - 1, cy + 1, highlight);
			set(cx + 1, cy + 1, highlight);
			set(cx - 1, cy + 3, highlight);
		}
		if (animName === 'attack') circle(cx + 4, cy, 2, hexToRgb('#FFFFFF'));
		if (animName === 'special') {
			// Invisibility shimmer / leap arc
			rect(cx - r, cy - 8, r * 2, 1, highlight);
		}
	} else if (style === 'cyclist') {
		const cx = size / 2;
		const cy = size / 2 + bob;
		// Wheels
		circle(cx, cy - 8, 4, body);
		circle(cx, cy + 8, 4, body);
		// Frame
		rect(cx - 1, cy - 8, 2, 16, accent);
		// Helmet
		circle(cx, cy - 10, 3, hexToRgb('#FF1F4B'));
		// Speed lines
		if (animName === 'walk' || animName === 'attack') {
			rect(0, cy - 12 + frameIndex, 6, 1, highlight);
			rect(0, cy + 10 - frameIndex, 6, 1, highlight);
		}
	} else if (style === 'leash_line') {
		// Horizontal red retractable leash across the frame
		rect(0, size / 2 - 1, size, 3, hexToRgb('#D04848'));
		// Handle on left, dog on right
		rect(0, size / 2 - 4, 6, 8, hexToRgb('#3A3A3A'));
		rect(size - 8, size / 2 - 4, 8, 8, hexToRgb('#7B4A1E'));
		if (animName === 'attack' || animName === 'special') rect(0, size / 2 - 1 - frameIndex, size, 1, hexToRgb('#FFFFFF'));
	} else if (style === 'coffee_splat') {
		const cx = size / 2;
		const cy = size / 2 + bob;
		circle(cx, cy, 10 + frameIndex, body);
		circle(cx, cy, 6, hexToRgb('#3A1F0A'));
		// Splat dots
		set(cx - 12, cy - 3, body);
		set(cx + 12, cy + 3, body);
		set(cx - 8, cy + 10, body);
	} else if (style === 'influencer') {
		const cx = size / 2;
		const cy = size / 2 + bob;
		// Body
		rect(cx - 8, cy - 4, 16, 14, body);
		// Head
		circle(cx, cy - 12, 6, hexToRgb('#F2C9A0'));
		// Hair (long blonde)
		rect(cx - 6, cy - 18, 12, 5, hexToRgb('#FFE066'));
		// Phone (separate hitbox visualized)
		rect(cx + 2, cy - 14, 4, 8, accent);
		// Phone screen
		rect(cx + 3, cy - 13, 2, 6, highlight);
		// Sunglasses
		rect(cx - 5, cy - 13, 10, 2, accent);
		// Selfie pose: arm out
		rect(cx + 6, cy - 13 + frameIndex, 2, 4, body);
		if (animName === 'attack') {
			// Flash
			circle(cx + 4, cy - 12, 4, hexToRgb('#FFFFFF'));
		}
	}
}

function buildSprite(spec) {
	const { id, dir, size, palette, style } = spec;
	const cols = Math.max(...FRAME_SET.map((f) => f.count));
	const rows = FRAME_SET.length;
	const sheet = new PNG({ width: cols * size, height: rows * size });
	// Transparent background
	for (let i = 0; i < sheet.data.length; i++) sheet.data[i] = 0;

	const frames = {};
	FRAME_SET.forEach((set, rowIdx) => {
		for (let i = 0; i < set.count; i++) {
			const x = i * size;
			const y = rowIdx * size;
			drawFrame(sheet, x, y, size, palette, style, set.name, i);
			frames[`${set.name}_${i}`] = {
				frame: { x, y, w: size, h: size },
				rotated: false,
				trimmed: false,
				spriteSourceSize: { x: 0, y: 0, w: size, h: size },
				sourceSize: { w: size, h: size },
				duration: 100
			};
		}
	});

	const outDir = join(ASSETS, dir);
	ensureDir(outDir);
	const png = PNG.sync.write(sheet);
	writeFileSync(join(outDir, `${id}.png`), png);

	const atlas = {
		frames,
		meta: {
			app: 'suburban-scramble placeholder generator',
			version: '1.0',
			image: `${id}.png`,
			format: 'RGBA8888',
			size: { w: cols * size, h: rows * size },
			scale: '1',
			frameTags: FRAME_SET.map((set, rowIdx) => ({
				name: set.name,
				from: rowIdx * cols,
				to: rowIdx * cols + set.count - 1,
				direction: 'forward'
			}))
		}
	};
	writeFileSync(join(outDir, `${id}.json`), JSON.stringify(atlas, null, 2));
	console.log(`✓ ${dir}/${id} (${cols * size}x${rows * size})`);
}

// 64x64 katy_trail tile — green/concrete pattern
function buildTile() {
	const TILE = 64;
	const png = new PNG({ width: TILE, height: TILE });
	for (let y = 0; y < TILE; y++) {
		for (let x = 0; x < TILE; x++) {
			const idx = (y * TILE + x) * 4;
			const isPath = x > 12 && x < 52;
			let r, g, b;
			if (isPath) {
				// Concrete with subtle noise
				const n = (x * 31 + y * 17) % 13;
				r = g = b = 180 + n;
			} else {
				// Grass with variation
				const n = (x * 7 + y * 5) % 21;
				r = 40 + (n % 7);
				g = 110 + n;
				b = 40 + (n % 5);
			}
			png.data[idx] = r;
			png.data[idx + 1] = g;
			png.data[idx + 2] = b;
			png.data[idx + 3] = 255;
		}
	}
	// Yellow center line
	for (let y = 0; y < TILE; y += 8) {
		for (let yy = 0; yy < 4; yy++) {
			const py = y + yy;
			if (py >= TILE) break;
			for (let xx = 30; xx < 34; xx++) {
				const idx = (py * TILE + xx) * 4;
				png.data[idx] = 240;
				png.data[idx + 1] = 200;
				png.data[idx + 2] = 30;
				png.data[idx + 3] = 255;
			}
		}
	}
	const outDir = join(ASSETS, 'tiles');
	ensureDir(outDir);
	writeFileSync(join(outDir, 'katy_trail.png'), PNG.sync.write(png));
	console.log('✓ tiles/katy_trail');
}

// 8x8 heart for HUD
function buildHeart() {
	const W = 16, H = 14;
	const png = new PNG({ width: W, height: H });
	for (let i = 0; i < png.data.length; i++) png.data[i] = 0;
	// Hand-drawn heart pixel pattern
	const pattern = [
		'..##..##..',
		'.######.##',
		'##########',
		'##########',
		'.########.',
		'..######..',
		'...####...',
		'....##....'
	];
	for (let y = 0; y < pattern.length; y++) {
		for (let x = 0; x < pattern[y].length; x++) {
			if (pattern[y][x] === '#') {
				const idx = (y * W + x) * 4;
				png.data[idx] = 230;
				png.data[idx + 1] = 50;
				png.data[idx + 2] = 70;
				png.data[idx + 3] = 255;
			}
		}
	}
	const outDir = join(ASSETS, 'ui');
	ensureDir(outDir);
	writeFileSync(join(outDir, 'heart.png'), PNG.sync.write(png));
	console.log('✓ ui/heart');
}

// Portraits — 64x64, single static frame matching character palette
function buildPortrait(spec) {
	const SIZE = 64;
	const png = new PNG({ width: SIZE, height: SIZE });
	for (let i = 0; i < png.data.length; i++) png.data[i] = 0;
	// Big static frame — reuse the drawFrame routine at 2x scale by drawing into an interim sprite
	const inner = new PNG({ width: 32, height: 32 });
	for (let i = 0; i < inner.data.length; i++) inner.data[i] = 0;
	drawFrame(inner, 0, 0, 32, spec.palette, spec.style, 'idle', 0);
	// Scale 2x
	for (let y = 0; y < 32; y++) {
		for (let x = 0; x < 32; x++) {
			const sIdx = (y * 32 + x) * 4;
			const r = inner.data[sIdx], g = inner.data[sIdx + 1], b = inner.data[sIdx + 2], a = inner.data[sIdx + 3];
			for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
				const dIdx = ((y * 2 + dy) * SIZE + (x * 2 + dx)) * 4;
				png.data[dIdx] = r;
				png.data[dIdx + 1] = g;
				png.data[dIdx + 2] = b;
				png.data[dIdx + 3] = a;
			}
		}
	}
	const outDir = join(ASSETS, 'ui', 'portraits');
	ensureDir(outDir);
	writeFileSync(join(outDir, `${spec.id}.png`), PNG.sync.write(png));
	console.log(`✓ ui/portraits/${spec.id}`);
}

ensureDir(ASSETS);
sprites.forEach(buildSprite);
sprites.filter((s) => s.dir === 'characters').forEach(buildPortrait);
buildTile();
buildHeart();
console.log('\nDone. Assets at static/assets/');
