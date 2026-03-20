import { getSongs } from '@/lib/songs';
import LibraryClient from '@/components/LibraryClient';

export default function Home() {
  const songs = getSongs().map(song => ({
    slug: song.slug,
    title: song.title,
  }));

  return <LibraryClient songs={songs} />;
}
