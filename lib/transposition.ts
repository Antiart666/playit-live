/**
 * Chord Transposition Logic
 * Mimics the Python logic from the original app.py
 */

const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

/**
 * Transpose a single chord by a given number of semitones
 * @param chord - The chord to transpose (e.g., "Am", "C", "G7")
 * @param steps - Number of semitones to transpose (can be negative)
 * @returns The transposed chord or the original if not recognized
 */
export function transposeChord(chord: string, steps: number): string {
  const match = chord.match(/^([A-G]#?)(.*)$/);
  if (!match) return chord;

  const [, root, suffix] = match;

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
