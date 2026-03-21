'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { AppBar, Toolbar, Box } from '@mui/material';
import styles from './Header.module.css';

interface HeaderProps {
  showBackButton?: boolean;
  onBack?: () => void;
  title?: string;
  titleClassName?: string;
  children?: React.ReactNode;
}

export default function Header({ showBackButton, onBack, title, titleClassName, children }: HeaderProps) {
  return (
    <AppBar position="fixed" className={styles.header}>
      <Toolbar className={styles.toolbar} disableGutters>
        {/* Center Title */}
        {title && <Box className={`${styles.title} ${titleClassName || ''}`}>{title}</Box>}

        {/* Right side controls */}
        <Box className={styles.controls}>
          {children}
          {showBackButton && (
            <Link
              href="/"
              onClick={onBack}
              className={styles.backLogoLink}
              aria-label="Till startsidan"
            >
              <Image
                src="/logo.png"
                alt="Playit"
                width={36}
                height={36}
                className={styles.backLogoIcon}
              />
            </Link>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}
