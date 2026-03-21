'use client';

import { ThemeProvider as MuiThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { ThemeProvider as CustomThemeProvider } from '@/lib/useTheme';

// Material Design 3 Black Stage Mode Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#000000',
      paper: '#1a1a1a',
    },
    primary: {
      main: '#D187FF', // Purple for accents
    },
    secondary: {
      main: '#ffffff',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b0b0',
    },
  },
  typography: {
    fontFamily: '"Courier New", Courier, monospace',
    body1: {
      fontSize: '16px',
      lineHeight: 1.5,
    },
    h1: {
      fontSize: '28px',
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'uppercase',
          fontWeight: 700,
          minHeight: '44px',
          minWidth: '44px',
        },
        contained: {
          backgroundColor: '#222222',
          color: '#ffffff',
          '&:hover': {
            backgroundColor: '#333333',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#000000',
          backgroundImage: 'none',
          borderBottom: '1px solid #1a1a1a',
          boxShadow: 'none',
        },
      },
    },
  },
});

interface ClientThemeProviderProps {
  children: React.ReactNode;
}

export default function ClientThemeProvider({ children }: ClientThemeProviderProps) {
  return (
    <CustomThemeProvider>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </CustomThemeProvider>
  );
}
