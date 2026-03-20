/**
 * Chord Formatter - Separates chords from lyrics for vertical alignment
 * Handles monospace alignment and mobile responsiveness
 */

export interface ChordPosition {
  chord: string;
  position: number; // Character position in the line
}

export interface FormattedLine {
  chords: ChordPosition[];
  lyrics: string; // Lyrics without chord brackets
}

/**
 * Parse a line of lyrics to extract chords and their positions
 * @param line - Single line of lyrics with chords in [brackets]
 * @returns Object with chord positions and clean lyrics
 */
export function parseChordLine(line: string): FormattedLine {
  const chords: ChordPosition[] = [];
  let cleanLyrics = '';
  let lastIndex = 0;

  // Regex to find chords in [brackets]
  const chordRegex = /\[([^\]]+)\]/g;
  let match;

  while ((match = chordRegex.exec(line)) !== null) {
    const chord = match[1];
    const chordStartInOriginal = match.index;

    // Add text before this chord
    const textBefore = line.substring(lastIndex, chordStartInOriginal);
    cleanLyrics += textBefore;

    // Record chord position based on where it appears in clean lyrics
    chords.push({
      chord,
      position: cleanLyrics.length,
    });

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  cleanLyrics += line.substring(lastIndex);

  return {
    chords,
    lyrics: cleanLyrics,
  };
}

/**
 * Build a chord line with proper spacing for monospace alignment
 * Each character position must align with the lyrics below
 * @param chordPositions - Array of chords and their positions
 * @param lyricsLength - Length of the lyrics line for reference
 * @returns Formatted chord line string
 */
export function buildChordLineSpacing(
  chordPositions: ChordPosition[],
  lyricsLength: number
): string {
  if (chordPositions.length === 0) {
    return ''; // No chords, return empty
  }

  // Create array to build the chord line character by character
  const chordLine: string[] = [];

  for (let i = 0; i < lyricsLength; i++) {
    chordLine[i] = ' '; // Default to space
  }

  // Place each chord at its position
  for (const { chord, position } of chordPositions) {
    const chordChars = chord.split('');
    for (let i = 0; i < chordChars.length && position + i < lyricsLength; i++) {
      chordLine[position + i] = chordChars[i];
    }
  }

  return chordLine.join('');
}

/**
 * Format entire lyrics text with chords separated above
 * Handles multiple lines and preserves structure
 * @param text - Full lyrics text with chords in [brackets]
 * @returns Array of {chordLine, lyricLine} pairs
 */
export function formatLyricsWithChordsAbove(
  text: string
): Array<{ chordLine: string; lyricLine: string }> {
  const lines = text.split('\n');
  const result: Array<{ chordLine: string; lyricLine: string }> = [];

  for (const line of lines) {
    if (line.trim().length === 0) {
      // Empty line - preserve it
      result.push({
        chordLine: '',
        lyricLine: line,
      });
      continue;
    }

    const parsed = parseChordLine(line);

    // Only show chord line if there are chords
    if (parsed.chords.length > 0) {
      const chordLine = buildChordLineSpacing(parsed.chords, parsed.lyrics.length);
      result.push({
        chordLine,
        lyricLine: parsed.lyrics,
      });
    } else {
      // No chords in this line
      result.push({
        chordLine: '',
        lyricLine: parsed.lyrics,
      });
    }
  }

  return result;
}

/**
 * Handle tabs and spacing for mobile display
 * Converts tabs to spaces for consistent monospace rendering
 * @param text - Text potentially containing tabs
 * @param tabWidth - Number of spaces per tab (default: 2 for compact mobile display)
 * @returns Text with tabs converted to spaces
 */
export function normalizeTabs(text: string, tabWidth: number = 2): string {
  return text.replace(/\t/g, ' '.repeat(tabWidth));
}
