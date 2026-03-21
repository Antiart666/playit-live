'use client';

import React, { useState, useMemo } from 'react';
import { Box, Button, Stack } from '@mui/material';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import SearchBar from '@/components/SearchBar';
import styles from './page.module.css';

interface LibrarySong {
  slug: string;
  title: string;
}

interface LibraryPageProps {
  songs: LibrarySong[];
}

export default function LibraryClient({ songs }: LibraryPageProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  // Filter songs based on search query
  const filteredSongs = useMemo(() => {
    if (!searchQuery.trim()) {
      return songs;
    }
    const query = searchQuery.toLowerCase();
    return songs.filter(song =>
      song.title.toLowerCase().includes(query)
    );
  }, [songs, searchQuery]);

  const handleSongClick = (slug: string) => {
    router.push(`/song/${slug}`);
  };

  return (
    <div className={styles.pageWrapper}>
      <Header title="Antichrister says playit!" />

      <Box className={styles.libraryContainer}>
        <SearchBar 
          onSearch={setSearchQuery}
          placeholder="Sök låtar..."
        />
        
        <Stack spacing={1} className={styles.songList}>
          {filteredSongs.length > 0 ? (
            filteredSongs.map(song => (
              <Button
                key={song.slug}
                onClick={() => handleSongClick(song.slug)}
                variant="contained"
                fullWidth
                className={styles.songButton}
              >
                {song.title}
              </Button>
            ))
          ) : (
            <Box className={styles.noResults}>
              Inga låtar hittades
            </Box>
          )}
        </Stack>
      </Box>
    </div>
  );
}
