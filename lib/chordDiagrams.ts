/**
 * Chord Diagrams Database
 * Visual representation of guitar chords
 * Each chord shows: frets, position, and finger placement
 */

export interface ChordDiagram {
  name: string;
  frets: number[]; // -1 = mute, 0 = open, 1-4 = fret number
  fingers: number[]; // 0 = not played, 1-4 = finger number
  baseFret: number; // Capo position if needed
  barFrets?: number[]; // For bar chords
}

export const CHORD_DIAGRAMS: Record<string, ChordDiagram> = {
  // Major chords
  C: {
    name: 'C',
    frets: [0, 3, 2, 0, 1, 0],
    fingers: [0, 3, 2, 0, 1, 0],
    baseFret: 0,
  },
  D: {
    name: 'D',
    frets: [-1, -1, 0, 2, 3, 2],
    fingers: [0, 0, 0, 1, 3, 2],
    baseFret: 0,
  },
  E: {
    name: 'E',
    frets: [0, 2, 2, 1, 0, 0],
    fingers: [0, 1, 2, 3, 0, 0],
    baseFret: 0,
  },
  F: {
    name: 'F',
    frets: [1, 3, 3, 2, 1, 1],
    fingers: [1, 3, 4, 2, 1, 1],
    baseFret: 1,
    barFrets: [0, 5],
  },
  G: {
    name: 'G',
    frets: [3, 2, 0, 0, 0, 3],
    fingers: [2, 1, 0, 0, 0, 3],
    baseFret: 0,
  },
  A: {
    name: 'A',
    frets: [0, 0, 2, 2, 2, 0],
    fingers: [0, 0, 1, 2, 3, 0],
    baseFret: 0,
  },
  B: {
    name: 'B',
    frets: [2, 4, 4, 4, 3, 2],
    fingers: [1, 3, 4, 2, 2, 1],
    baseFret: 2,
    barFrets: [0, 5],
  },

  // Minor chords
  Am: {
    name: 'Am',
    frets: [0, 0, 2, 2, 1, 0],
    fingers: [0, 0, 2, 3, 1, 0],
    baseFret: 0,
  },
  Dm: {
    name: 'Dm',
    frets: [-1, -1, 0, 2, 3, 1],
    fingers: [0, 0, 0, 1, 3, 2],
    baseFret: 0,
  },
  Em: {
    name: 'Em',
    frets: [0, 2, 2, 0, 1, 0],
    fingers: [0, 1, 2, 0, 3, 0],
    baseFret: 0,
  },
  Bm: {
    name: 'Bm',
    frets: [2, 3, 4, 4, 3, 2],
    fingers: [1, 2, 3, 4, 2, 1],
    baseFret: 2,
    barFrets: [0, 5],
  },

  // Dominant7 chords
  'G7': {
    name: 'G7',
    frets: [3, 2, 0, 0, 0, 1],
    fingers: [3, 1, 0, 0, 0, 2],
    baseFret: 0,
  },
  'C7': {
    name: 'C7',
    frets: [0, 3, 2, 3, 1, 0],
    fingers: [0, 2, 1, 3, 1, 0],
    baseFret: 0,
  },

  // Major7 chords
  'Cmaj7': {
    name: 'Cmaj7',
    frets: [0, 3, 2, 0, 0, 0],
    fingers: [0, 2, 1, 0, 0, 0],
    baseFret: 0,
  },

  // Minor7 chords
  'Am7': {
    name: 'Am7',
    frets: [0, 0, 2, 0, 1, 0],
    fingers: [0, 0, 2, 0, 1, 0],
    baseFret: 0,
  },
};

/**
 * Get chord diagram by name (handles transposition)
 * Maps transposed chords back to standard fingering patterns
 */
export function getChordDiagram(chordName: string): ChordDiagram | null {
  // Direct match
  if (CHORD_DIAGRAMS[chordName]) {
    return CHORD_DIAGRAMS[chordName];
  }

  // Try to find similar pattern (for transposed chords)
  // For now, just return null for unknown chords
  return null;
}

/**
 * Get all available chord names
 */
export function getAvailableChords(): string[] {
  return Object.keys(CHORD_DIAGRAMS);
}
