/**
 * Chord Transposition Logic
 * Mimics the Python logic from the original app.py
 */

const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const FLAT_TO_SHARP: Record<string, string> = {
  Db: 'C#',
  Eb: 'D#',
  Gb: 'F#',
  Ab: 'G#',
  Bb: 'A#',
};

function normalizeNote(note: string): string {
  return FLAT_TO_SHARP[note] || note;
}

export function isChordToken(token: string): boolean {
  const cleaned = token.trim();
  if (!cleaned) return false;
  if (cleaned.includes('|') || cleaned.includes('---')) return false;

  return /^([A-G](?:#|b)?)(?:(?:maj|min|dim|aug|sus|add|m|M)?[0-9]*(?:[#b][0-9]+)*(?:\/[A-G](?:#|b)?)?)?(?:\([^)]+\))?$/.test(cleaned);
}

function transposeChordToken(chord: string, steps: number): string {
  const transposed = transposeChord(chord, steps);
  return transposed.replace(/\/([A-G](?:#|b)?)/g, (_match, bassNote) => `/${transposeChord(bassNote, steps)}`);
}

function transposeChordsInSegment(segment: string, steps: number): string {
  return segment.replace(/\b([A-G](?:#|b)?(?:[^\s\]]*)?)\b/g, (token) => {
    return isChordToken(token) ? transposeChordToken(token, steps) : token;
  });
}

function isChordOnlyLine(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed) return false;
  if (/^[A-Ga-g]\s*\|/.test(trimmed) || trimmed.includes('|---')) return false;

  const tokens = trimmed.split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return false;

  let relevant = 0;
  let chordLike = 0;

  for (const rawToken of tokens) {
    const token = rawToken.replace(/[.,;:!?]+$/g, '');
    if (/^\(x\d+\)$/i.test(token) || /^x\d+$/i.test(token)) {
      continue;
    }

    relevant += 1;
    if (isChordToken(token)) {
      chordLike += 1;
    }
  }

  if (relevant === 0) return false;
  return chordLike > 0 && chordLike / relevant >= 0.6;
}

/**
 * Transpose a single chord by a given number of semitones
 * @param chord - The chord to transpose (e.g., "Am", "C", "G7")
 * @param steps - Number of semitones to transpose (can be negative)
 * @returns The transposed chord or the original if not recognized
 */
export function transposeChord(chord: string, steps: number): string {
  const match = chord.match(/^([A-G](?:#|b)?)(.*)$/);
  if (!match) return chord;

  const [, rawRoot, suffix] = match;
  const root = normalizeNote(rawRoot);

  if (!NOTES.includes(root)) return chord;

  const rootIndex = NOTES.indexOf(root);
  const newIndex = (rootIndex + steps) % 12;
  const newRoot = NOTES[newIndex >= 0 ? newIndex : newIndex + 12];

  return `${newRoot}${suffix}`;
}

/**
 * Process lyrics with chord transposition
 * Finds all chords in [bracket] format and transposes them
 * @param text - The lyrics text with chords in brackets
 * @param steps - Number of semitones to transpose
 * @returns Array of text and chord elements for rendering
 */
export function processLyrics(text: string, steps: number): Array<{ type: 'chord' | 'text'; content: string }> {
  // First, transpose all chords
  let transposed = text.replace(/\[(.*?)\]/g, (_match, chord) => {
    const transposedChord = transposeChord(chord.trim(), steps);
    return `[${transposedChord}]`;
  });

  // Then, split by chords
  const parts = transposed.split(/(\[.*?\])/);

  return parts
    .filter(part => part.length > 0)
    .map(part => ({
      type: part.match(/^\[.*\]$/) ? 'chord' : 'text',
      content: part,
    }));
}

export function transposeSongContent(text: string, steps: number): string {
  if (steps === 0) return text;

  const lines = text.split('\n').map((line) => {
    const withBracketedChords = line.replace(/\[([^\]]+)\]/g, (_match, inner) => {
      return `[${transposeChordsInSegment(inner, steps)}]`;
    });

    if (isChordOnlyLine(withBracketedChords)) {
      return transposeChordsInSegment(withBracketedChords, steps);
    }

    return withBracketedChords;
  });

  return lines.join('\n');
}
