import type { CharacterId, CharacterStats, VisualSpec } from '../types';

export const CHARACTER_IDS: CharacterId[] = ['rosie', 'katie', 'charlie', 'nancy', 'tia'];

export const CHARACTER_STATS: Record<CharacterId, CharacterStats> = {
	rosie: { speed: 1.5, hp: 2, special: 'zoomies', attack: 'sonicBark' },
	katie: { speed: 1.0, hp: 3, special: 'privacyBubble', attack: 'watchLaser' },
	charlie: { speed: 0.7, hp: 5, special: 'bunker', attack: 'groundStomp' },
	nancy: { speed: 1.2, hp: 3, special: 'invisibility', attack: 'clawSwipe' },
	tia: { speed: 1.1, hp: 3, special: 'fenceLeap', attack: 'tailWhip' }
};

export const CHARACTER_NAMES: Record<CharacterId, string> = {
	rosie: 'Rosie',
	katie: 'Katie',
	charlie: 'Charlie',
	nancy: 'Nancy',
	tia: 'Tia'
};

export const CHARACTER_BLURBS: Record<CharacterId, string> = {
	rosie: 'Border collie. Tennis-ball obsessed. Fast and fragile.',
	katie: 'The walker. Pink Lululemon. Apple-Watch laser. Just wants 10k steps.',
	charlie: 'Border collie tank. Tri-color. Defends the cul-de-sac.',
	nancy: 'Earl-grey kitten. Skittish but lethal up close.',
	tia: 'Confident grey tabby. Older sister energy. Leaps over anything.'
};

export const CHARACTER_VISUALS: Record<CharacterId, VisualSpec> = {
	rosie: {
		species: 'border_collie',
		palette: ['#000000', '#FFFFFF'],
		build: 'lean',
		notes: 'classic black/white BC, white blaze, amber eyes'
	},
	charlie: {
		species: 'border_collie',
		palette: ['#000000', '#FFFFFF', '#7B4A1E'],
		build: 'stocky',
		notes: 'tri-color BC: kabuki brows, looks like collie x GSD x Bernese'
	},
	katie: {
		species: 'human',
		palette: ['#F8B6CB', '#3A2B22', '#FFFFFF'],
		build: 'human_athleisure',
		notes: 'brunette ponytail, pink Lululemon, Apple Watch'
	},
	tia: {
		species: 'cat',
		palette: ['#8C8F95', '#FFFFFF'],
		build: 'large_confident',
		notes: 'earl grey + white, older, bigger, half-lidded gaze'
	},
	nancy: {
		species: 'cat',
		palette: ['#A6A8AC', '#FFFFFF'],
		build: 'small_skittish',
		notes: 'earl grey + white, smaller, leggier, big alert eyes'
	}
};
