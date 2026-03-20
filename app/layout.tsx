import type { Metadata } from 'next';
import ClientThemeProvider from '@/components/ClientThemeProvider';
import './globals.css';

export const metadata: Metadata = {
  title: 'Antichrister says playit!',
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
      <body>
        <ClientThemeProvider>
          {children}
        </ClientThemeProvider>
      </body>
    </html>
  );
}
