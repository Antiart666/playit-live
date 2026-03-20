'use client';

import React, { useState } from 'react';
import { Popover, Box } from '@mui/material';
import ChordDiagram from '@/components/ChordDiagram';
import styles from './ChordLine.module.css';

interface ChordLineProps {
  chordLine: string;
  lyricLine: string;
  lineNumber?: number;
}

/**
 * ChordLine Component
 * Renders a single line of lyrics with chords displayed above in monospace alignment
 * Chords are clickable and show diagrams in a popup
 */
export default function ChordLine({
  chordLine,
  lyricLine,
  lineNumber,
}: ChordLineProps) {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [selectedChord, setSelectedChord] = useState<string | null>(null);

  // Handle empty lines
  if (!lyricLine.trim()) {
    return <div className={styles.emptyLine}>{lyricLine}</div>;
  }

  const handleChordClick = (
    e: React.MouseEvent<HTMLSpanElement>,
    chord: string
  ) => {
    setSelectedChord(chord);
    setAnchorEl(e.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setSelectedChord(null);
  };

  const open = Boolean(anchorEl);

  // Make chords clickable
  const renderChordLine = () => {
    if (!chordLine || chordLine.trim().length === 0) {
      return null;
    }

    // Split by words and find chords
    const words = chordLine.split(' ');
    return words.map((word, idx) => {
      // If word appears to be a chord (starts with a letter and contains only letters, #, digits, etc.)
      if (word.match(/^[A-Gb#m\d\-sus]+$/i)) {
        return (
          <span
            key={idx}
            className={styles.chordClickable}
            onClick={e => handleChordClick(e, word)}
          >
            {word}
          </span>
        );
      }
      return (
        <span key={idx} className={styles.chordWord}>
          {word}
        </span>
      );
    });
  };

  return (
    <div className={styles.container} key={`line-${lineNumber}`}>
      {/* Chord line - only show if there are chords */}
      {chordLine && chordLine.trim().length > 0 && (
        <pre className={styles.chordLine}>{renderChordLine()}</pre>
      )}

      {/* Lyric line */}
      <pre className={styles.lyricLine}>{lyricLine}</pre>

      {/* Chord Diagram Popup */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
      >
        <Box className={styles.popover}>
          {selectedChord && <ChordDiagram chordName={selectedChord} size="medium" />}
        </Box>
      </Popover>
    </div>
  );
}
