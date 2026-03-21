'use client';

import React, { useState, useMemo } from 'react';
import Image from 'next/image';
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
  const [isListOpen, setIsListOpen] = useState(false);
  const songListRef = React.useRef<HTMLDivElement | null>(null);

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

  const toggleList = () => {
    setIsListOpen(prev => !prev);
  };

  const handleLogoClick = () => {
    if (!isListOpen) {
      setIsListOpen(true);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          songListRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
      });
      return;
    }

    songListRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className={styles.pageWrapper}>
      <Header title="Antichrister says playit!" titleClassName={styles.homeTitle}>
        <Button
          onClick={toggleList}
          variant="contained"
          size="small"
          className={styles.toggleButton}
        >
          {isListOpen ? 'STANG' : 'LATLISTA'}
        </Button>
      </Header>

      <Box className={styles.heroSection}>
        <button
          type="button"
          onClick={handleLogoClick}
          className={styles.logoButton}
          aria-label="Öppna låtlistan"
        >
          <Image
            src="/logo.png"
            alt="Playit logga"
            width={360}
            height={520}
            priority
            className={styles.logoImage}
          />
        </button>
      </Box>

      <Box className={styles.libraryContainer} ref={songListRef}>
        {isListOpen && (
          <Box className={styles.dropdownPanel}>
            <SearchBar
              onSearch={setSearchQuery}
              placeholder="Sok latar..."
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
                  Inga latar hittades
                </Box>
              )}
            </Stack>
          </Box>
        )}
      </Box>
    </div>
  );
}
