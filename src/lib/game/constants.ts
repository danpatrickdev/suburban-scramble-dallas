// Wider portrait so the canvas fills more of the screen and there's room for
// more enemies on screen at once. Aspect 9:14 (~0.64) — a bit wider than 9:16
// so it doesn't feel like a phone strip.
export const GAME_WIDTH = 540;
export const GAME_HEIGHT = 840;

export const BASE_SCROLL_SPEED = 90; // px/sec
export const SCROLL_RAMP_PER_SEC = 1.6; // additive px/sec each second
export const MAX_SCROLL_SPEED = 260;

export const PLAYER_BASE_SPEED = 170; // px/sec
export const PLAYER_HITBOX_RADIUS = 9;

export const PROJECTILE_SPEED = 380;
export const SONIC_BARK_RADIUS_MAX = 80;
export const SONIC_BARK_DURATION = 360; // ms

export const SPECIAL_COOLDOWN = 8000; // ms
export const ATTACK_COOLDOWN = 280; // ms

export const FRENZY_KILLS_REQUIRED = 5;
export const FRENZY_DURATION = 5000; // ms

export const KATY_TRAIL_LENGTH_MS = 90_000; // 90s to boss
export const KATY_TRAIL_SPEED_MOD = 1.2;

export const STORAGE_KEYS = {
	unlockedCharacters: 'ssd:unlocked_characters',
	highScores: 'ssd:high_scores',
	totalTreats: 'ssd:total_treats',
	lastCharacter: 'ssd:last_character'
} as const;
