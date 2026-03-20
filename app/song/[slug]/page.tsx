'use client';

import React from 'react';
import { useRouter, useParams } from 'next/navigation';
import Header from '@/components/Header';
import SongContent from '@/components/SongContent';

export default function SongPage() {
  const [songData, setSongData] = React.useState<{ content: string; title: string } | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const slug = params?.slug as string;

  React.useEffect(() => {
    if (!slug) return;
    
    // Fetch song data from an API route
    fetch(`/api/songs/${slug}`)
      .then(res => {
        if (!res.ok) {
          throw new Error('Song not found');
        }
        return res.json();
      })
      .then(data => {
        setSongData(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [slug]);

  const handleBack = () => {
    router.push('/');
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error || !songData) {
    return <div>Error: {error || 'Song not found'}</div>;
  }

  return (
    <>
      <Header
        title={songData.title}
        showBackButton
        onBack={handleBack}
      />
      <SongContent content={songData.content} />
    </>
  );
}
