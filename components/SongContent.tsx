'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, ButtonGroup, IconButton, Popover, Stack, Slider, Typography } from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';
import { transposeChord } from '@/lib/transposition';
import { formatLyricsWithChordsAbove, normalizeTabs } from '@/lib/chordFormatter';
import ChordLine from '@/components/ChordLine';
import styles from './SongContent.module.css';

interface SongContentProps {
  content: string;
}

export default function SongContent({ content }: SongContentProps) {
  const [transpose, setTranspose] = useState(0);
  const [scrolling, setScrolling] = useState(false);
  const [speed, setSpeed] = useState(40);
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
  const scrollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Transpose all chords in the content
   */
  const transposeContent = (text: string, steps: number): string => {
    if (steps === 0) return text;
    return text.replace(/\[([^\]]+)\]/g, (_match, chord) => {
      const transposedChord = transposeChord(chord.trim(), steps);
      return `[${transposedChord}]`;
    });
  };

  // Normalize tabs and transpose
  const normalizedContent = normalizeTabs(content, 2);
  const transposedContent = transposeContent(normalizedContent, transpose);
  const formattedLines = formatLyricsWithChordsAbove(transposedContent);

  // Handle autoscroll
  useEffect(() => {
    if (scrolling) {
      // Inverse speed: higher speed means faster scroll
      const ms = Math.max(10, Math.floor(150 - speed));
      scrollIntervalRef.current = setInterval(() => {
        window.scrollBy(0, 1);
      }, ms);
    } else {
      if (scrollIntervalRef.current) {
        clearInterval(scrollIntervalRef.current);
      }
    }

    return () => {
      if (scrollIntervalRef.current) {
        clearInterval(scrollIntervalRef.current);
      }
    };
  }, [scrolling, speed]);

  const handlePopoverOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <>
      {/* Fixed Control Panel */}
      <Box className={styles.controlPanel}>
        <div className={styles.controlGroup}>
          <Typography variant="caption" className={styles.label}>
            TON: {transpose}
          </Typography>
          <ButtonGroup size="small" variant="contained">
            <Button onClick={() => setTranspose(transpose - 1)} className={styles.controlButton}>
              −
            </Button>
            <Button onClick={() => setTranspose(0)} className={styles.controlButton}>
              STD
            </Button>
            <Button onClick={() => setTranspose(transpose + 1)} className={styles.controlButton}>
              +
            </Button>
          </ButtonGroup>
        </div>

        <IconButton
          onClick={handlePopoverOpen}
          className={styles.settingsButton}
          size="small"
        >
          <TuneIcon />
        </IconButton>

        <Popover
          open={open}
          anchorEl={anchorEl}
          onClose={handlePopoverClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          className={styles.popover}
        >
          <Box className={styles.popoverContent}>
            <Stack spacing={2}>
              <Typography variant="subtitle2">SCROLL CONTROLS</Typography>

              <Box>
                <Typography variant="caption">AUTOSCROLL</Typography>
                <Button
                  onClick={() => setScrolling(!scrolling)}
                  variant={scrolling ? 'contained' : 'outlined'}
                  size="small"
                  fullWidth
                  className={styles.toggleButton}
                >
                  {scrolling ? 'ON' : 'OFF'}
                </Button>
              </Box>

              <Box>
                <Typography variant="caption">FART: {speed}</Typography>
                <Slider
                  value={speed}
                  onChange={(_, value) => setSpeed(value as number)}
                  min={1}
                  max={100}
                  className={styles.slider}
                />
              </Box>
            </Stack>
          </Box>
        </Popover>
      </Box>

      {/* Lyrics Content */}
      <Box className={styles.lyricsContainer}>
        <Box className={styles.lyrics}>
          {formattedLines.map((line, idx) => (
            <ChordLine
              key={idx}
              lineNumber={idx}
              chordLine={line.chordLine}
              lyricLine={line.lyricLine}
            />
          ))}
        </Box>
      </Box>
    </>
  );
}
