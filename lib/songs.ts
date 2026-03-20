import fs from 'fs';
import path from 'path';

const LIBRARY_DIR = path.join(process.cwd(), 'library');

export interface Song {
  slug: string;
  title: string;
  path: string;
}

/**
 * Get all songs from the library directory
 */
export function getSongs(): Song[] {
  if (!fs.existsSync(LIBRARY_DIR)) {
    return [];
  }

  const files = fs.readdirSync(LIBRARY_DIR).filter(file => file.endsWith('.md'));

  return files
    .sort()
    .map(file => {
      const slug = file.replace('.md', '');
      const title = slug.replace(/_/g, ' ').toUpperCase();
      return {
        slug,
        title,
        path: path.join(LIBRARY_DIR, file),
      };
    });
}

/**
 * Get a single song by slug
 */
export function getSongBySlug(slug: string): { content: string; title: string } | null {
  const songs = getSongs();
  const song = songs.find(s => s.slug === slug);

  if (!song) {
    return null;
  }

  try {
    const content = fs.readFileSync(song.path, 'utf-8');
    return {
      content,
      title: song.title,
    };
  } catch (e) {
    console.error(`Failed to read song: ${slug}`, e);
    return null;
  }
}
