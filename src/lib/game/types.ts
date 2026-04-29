export type CharacterId = 'rosie' | 'katie' | 'charlie' | 'nancy' | 'tia';

export type AttackId =
	| 'sonicBark'
	| 'watchLaser'
	| 'groundStomp'
	| 'clawSwipe'
	| 'tailWhip';

export type SpecialId =
	| 'zoomies'
	| 'privacyBubble'
	| 'bunker'
	| 'invisibility'
	| 'fenceLeap';

export interface CharacterStats {
	speed: number; // multiplier on PLAYER_BASE_SPEED
	hp: number;
	special: SpecialId;
	attack: AttackId;
}

export interface VisualSpec {
	species: 'border_collie' | 'cat' | 'human';
	palette: string[];
	build: string;
	notes: string;
}

export type LevelId =
	| 'driveway'
	| 'katy_trail'
	| 'lower_greenville'
	| 'highland_park'
	| 'evoque_run'
	| 'fourth_of_july'
	| 'northlake';

export type EnemyKind = 'peloton' | 'leash' | 'coffee' | 'main_character_follower';

export interface WaveDef {
	at: number; // ms from level start
	kind: EnemyKind;
	count: number;
	pattern?: 'line' | 'spread' | 'random';
}

export interface DialogueLine {
	character: CharacterId | 'narrator' | 'enemy';
	portrait: string; // path under /assets/ui/portraits/
	text: string;
}

export interface DialogueTrigger {
	at: number; // ms from level start; -1 = on level start; -2 = on boss spawn
	line: DialogueLine;
	character?: CharacterId; // if set, only fire when this character is selected
}

export interface LevelDef {
	id: LevelId;
	title: string;
	tileKey: string;
	tilePath: string;
	speedMod: number;
	durationMs: number;
	waves: WaveDef[];
	dialogue: DialogueTrigger[];
	bossKey: 'main_character';
}
