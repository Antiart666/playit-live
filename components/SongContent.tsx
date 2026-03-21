'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, ButtonGroup, IconButton, Popover, Stack, Slider, Typography } from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';
import { transposeSongContent } from '@/lib/transposition';
import { formatLyricsWithChordsAbove, normalizeTabs } from '@/lib/chordFormatter';
import ChordLine from '@/components/ChordLine';
import styles from './SongContent.module.css';

interface SongContentProps {
  content: string;
  bpm: number;
}

export default function SongContent({ content, bpm }: SongContentProps) {
  const [transpose, setTranspose] = useState(0);
  const [scrolling, setScrolling] = useState(false);
  const [speedMultiplier, setSpeedMultiplier] = useState(100);
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
  const scrollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Normalize tabs and transpose
  const normalizedContent = normalizeTabs(content, 2);
  const transposedContent = transposeSongContent(normalizedContent, transpose);
  const formattedLines = formatLyricsWithChordsAbove(transposedContent);
  const effectiveBpm = Math.max(1, Math.round((bpm * speedMultiplier) / 100));

  // Handle autoscroll
  useEffect(() => {
    if (scrolling) {
      const intervalMs = 50;
      const pixelsPerBeat = 6;
      const pixelsPerSecond = (effectiveBpm / 60) * pixelsPerBeat;
      const pixelsPerTick = Math.max(0.25, pixelsPerSecond * (intervalMs / 1000));

      scrollIntervalRef.current = setInterval(() => {
        document.documentElement.scrollTop += pixelsPerTick;
        document.body.scrollTop += pixelsPerTick;
      }, intervalMs);
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
  }, [scrolling, effectiveBpm]);

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
                <Typography variant="caption">BPM: {bpm}</Typography>
                <Typography variant="caption" display="block">
                  EFFEKTIVT TEMPO: {effectiveBpm} BPM
                </Typography>
              </Box>

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
                <Typography variant="caption">
                  BPM-MULTIPLIKATOR: {(speedMultiplier / 100).toFixed(2)}x
                </Typography>
                <Slider
                  value={speedMultiplier}
                  onChange={(_, value) => setSpeedMultiplier(value as number)}
                  min={1}
                  max={150}
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
