'use client';

import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import styles from './SearchBar.module.css';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export default function SearchBar({ onSearch, placeholder = 'Sök låtar...' }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    onSearch(value);
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <Box className={styles.container}>
      <TextField
        fullWidth
        placeholder={placeholder}
        value={query}
        onChange={handleChange}
        variant="outlined"
        size="small"
        className={styles.input}
        InputProps={{
          startAdornment: <SearchIcon className={styles.icon} />,
          endAdornment: query && (
            <Button 
              onClick={handleClear} 
              className={styles.clearButton}
              size="small"
            >
              <ClearIcon fontSize="small" />
            </Button>
          ),
        }}
      />
    </Box>
  );
}
