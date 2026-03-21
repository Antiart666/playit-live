import fs from 'fs';
import path from 'path';

const LIBRARY_DIR = path.join(process.cwd(), 'library');

export interface Song {
  slug: string;
  title: string;
  path: string;
}

const DEFAULT_BPM = 100;

function extractMetadataBlock(content: string): string {
  const frontmatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---\s*/);
  if (frontmatterMatch?.[1]) {
    return frontmatterMatch[1];
  }

  const lines = content.split(/\r?\n/).slice(0, 30);
  const metadataLines: string[] = [];

  for (const line of lines) {
    if (!line.trim()) {
      break;
    }
    metadataLines.push(line);
  }

  return metadataLines.join('\n');
}

function extractBpmFromMetadata(content: string): number {
  const metadata = extractMetadataBlock(content);

  const bpmLabelMatch = metadata.match(/\bBPM\s*[:=]\s*~?\s*(\d+(?:\.\d+)?)/i);
  if (bpmLabelMatch?.[1]) {
    return Math.round(Number(bpmLabelMatch[1]));
  }

  const tempoLabelMatch = metadata.match(/\bTEMPO\b\s*[:=][^\n]*?(\d+(?:\.\d+)?)/i);
  if (tempoLabelMatch?.[1]) {
    return Math.round(Number(tempoLabelMatch[1]));
  }

  return DEFAULT_BPM;
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
export function getSongBySlug(slug: string): { content: string; title: string; bpm: number } | null {
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
      bpm: extractBpmFromMetadata(content),
    };
  } catch (e) {
    console.error(`Failed to read song: ${slug}`, e);
    return null;
  }
}
