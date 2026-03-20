'use client';

import React from 'react';
import { AppBar, Toolbar, Box, Button } from '@mui/material';
import Image from 'next/image';
import Link from 'next/link';
import styles from './Header.module.css';

interface HeaderProps {
  showBackButton?: boolean;
  onBack?: () => void;
  title?: string;
  children?: React.ReactNode;
}

export default function Header({ showBackButton, onBack, title, children }: HeaderProps) {
  return (
    <AppBar position="fixed" className={styles.header}>
      <Toolbar className={styles.toolbar} disableGutters>
        {/* Logo */}
        <Box className={styles.logoContainer}>
          <Link href="/">
            <Image
              src="/logo.png"
              alt="PlayIt! Logo"
              width={125}
              height={40}
              priority
              className={styles.logo}
            />
          </Link>
        </Box>

        {/* Center Title */}
        {title && <Box className={styles.title}>{title}</Box>}

        {/* Right side controls */}
        <Box className={styles.controls}>
          {children}
          {showBackButton && (
            <Button
              onClick={onBack}
              variant="contained"
              size="small"
              className={styles.backButton}
            >
              ⬅ LÅTAR
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}
