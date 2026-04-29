export type DifficultyId = 'beginner' | 'intermediate' | 'hard' | 'x_games';

export interface DifficultyMod {
	label: string;
	tagline: string;
	color: string;
	enemyCountMult: number;     // how many MORE enemies per wave
	enemySpeedMult: number;      // base scroll speed multiplier
	waveFrequencyMult: number;   // scales spawn cadence (interpolates new waves)
	playerHpBonus: number;
	bossHpMult: number;
}

export const DIFFICULTIES: Record<DifficultyId, DifficultyMod> = {
	beginner: {
		label: 'Beginner',
		tagline: 'Easy stroll. Few enemies, slow scroll.',
		color: '#88e1ff',
		enemyCountMult: 0.6,
		enemySpeedMult: 0.8,
		waveFrequencyMult: 0.7,
		playerHpBonus: 1,
		bossHpMult: 0.7
	},
	intermediate: {
		label: 'Intermediate',
		tagline: 'A normal Tuesday.',
		color: '#ffd500',
		enemyCountMult: 1.0,
		enemySpeedMult: 1.0,
		waveFrequencyMult: 1.0,
		playerHpBonus: 0,
		bossHpMult: 1.0
	},
	hard: {
		label: 'Hard',
		tagline: 'It is not a normal Tuesday.',
		color: '#ff8a3c',
		enemyCountMult: 1.6,
		enemySpeedMult: 1.18,
		waveFrequencyMult: 1.4,
		playerHpBonus: 0,
		bossHpMult: 1.4
	},
	x_games: {
		label: 'X Games',
		tagline: 'You will lose. That is the point.',
		color: '#ff3b5c',
		enemyCountMult: 2.6,
		enemySpeedMult: 1.45,
		waveFrequencyMult: 2.2,
		playerHpBonus: 0,
		bossHpMult: 2.0
	}
};

export const DIFFICULTY_ORDER: DifficultyId[] = ['beginner', 'intermediate', 'hard', 'x_games'];
