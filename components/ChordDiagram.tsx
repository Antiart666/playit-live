'use client';

import React from 'react';
import { Box, Tooltip } from '@mui/material';
import { getChordDiagram } from '@/lib/chordDiagrams';
import styles from './ChordDiagram.module.css';

interface ChordDiagramProps {
  chordName: string;
  size?: 'small' | 'medium' | 'large';
  interactive?: boolean;
}

const STRING_NAMES = ['E', 'B', 'G', 'D', 'A', 'E'];

/**
 * ChordDiagram - Visual guitar chord representation
 * Shows a 6-string guitar diagram with finger positions
 */
export default function ChordDiagram({
  chordName,
  size = 'medium',
  interactive = true,
}: ChordDiagramProps) {
  const diagram = getChordDiagram(chordName);

  if (!diagram) {
    return (
      <Box className={`${styles.container} ${styles[size]}`}>
        <div className={styles.noChord}>{chordName}</div>
      </Box>
    );
  }

  const strings = 6;
  const frets = 4;
  const cellSize = size === 'small' ? 20 : size === 'medium' ? 30 : 40;

  return (
    <Box
      className={`${styles.container} ${styles[size]} ${
        interactive ? styles.interactive : ''
      }`}
      title={chordName}
    >
      <div className={styles.diagram}>
        {/* Nut or fret indicator */}
        <div className={styles.fretIndicator}>
          {diagram.baseFret === 0 ? (
            <div className={styles.nut} />
          ) : (
            <div className={styles.fretNumber}>{diagram.baseFret}</div>
          )}
        </div>

        {/* Guitar strings & frets grid */}
        <svg
          width={strings * cellSize + 4}
          height={frets * cellSize + 20}
          className={styles.svg}
        >
          {/* Fret lines */}
          {[...Array(frets + 1)].map((_, fretIdx) => (
            <line
              key={`fret-${fretIdx}`}
              x1="2"
              y1={10 + fretIdx * cellSize}
              x2={strings * cellSize + 2}
              y2={10 + fretIdx * cellSize}
              stroke="#444444"
              strokeWidth="1"
            />
          ))}

          {/* String lines */}
          {[...Array(strings)].map((_, stringIdx) => (
            <line
              key={`string-${stringIdx}`}
              x1={2 + stringIdx * cellSize}
              y1="10"
              x2={2 + stringIdx * cellSize}
              y2={10 + frets * cellSize}
              stroke="#666666"
              strokeWidth="2"
            />
          ))}

          {/* Open/Mute indicators */}
          {diagram.frets.map((fret, stringIdx) => {
            if (fret === 0) {
              // Open string indicator
              return (
                <circle
                  key={`open-${stringIdx}`}
                  cx={2 + stringIdx * cellSize}
                  cy="0"
                  r="4"
                  fill="none"
                  stroke="#D187FF"
                  strokeWidth="2"
                />
              );
            } else if (fret === -1) {
              // Mute indicator
              return (
                <text
                  key={`mute-${stringIdx}`}
                  x={2 + stringIdx * cellSize}
                  y="8"
                  textAnchor="middle"
                  fontSize="12"
                  fill="#888888"
                  fontWeight="bold"
                >
                  ✕
                </text>
              );
            }
            return null;
          })}

          {/* Finger positions */}
          {diagram.frets.map((fret, stringIdx) => {
            if (fret > 0) {
              const y = 10 + (fret - 1) * cellSize + cellSize / 2;
              const x = 2 + stringIdx * cellSize;
              return (
                <Tooltip
                  key={`fret-${stringIdx}-${fret}`}
                  title={`String ${STRING_NAMES[stringIdx]}, Fret ${fret}`}
                >
                  <circle
                    cx={x}
                    cy={y}
                    r={cellSize / 2.5}
                    fill="#D187FF"
                    opacity="0.8"
                  />
                </Tooltip>
              );
            }
            return null;
          })}
        </svg>

        {/* Fret numbers */}
        <div className={styles.fretNumbers}>
          {[...Array(frets)].map((_, i) => (
            <span key={`fret-label-${i}`} className={styles.fretLabel}>
              {i + 1}
            </span>
          ))}
        </div>

        {/* String names */}
        <div className={styles.stringNames}>
          {STRING_NAMES.map((name, idx) => (
            <span key={`string-${idx}`} className={styles.stringName}>
              {name}
            </span>
          ))}
        </div>
      </div>

      {/* Chord name */}
      <div className={styles.chordName}>{chordName}</div>
    </Box>
  );
}
