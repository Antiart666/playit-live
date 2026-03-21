import type { Metadata } from 'next';
import { Quicksand, Fredoka } from 'next/font/google';
import ClientThemeProvider from '@/components/ClientThemeProvider';
import './globals.css';

const quicksand = Quicksand({
  subsets: ['latin'],
  variable: '--font-primary',
  weight: ['400', '500', '700'],
  display: 'swap',
});

const fredoka = Fredoka({
  subsets: ['latin'],
  variable: '--font-fallback',
  weight: ['400', '700'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Antichrister says PlayIt!',
  description: 'Music transposition app with Material Design 3',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </head>
      <body className={`${quicksand.variable} ${fredoka.variable}`}>
        <ClientThemeProvider>
          {children}
        </ClientThemeProvider>
      </body>
    </html>
  );
}
