import { getSongBySlug } from '@/lib/songs';
import { NextResponse } from 'next/server';

interface RouteParams {
  params: Promise<{ slug: string }>;
}

export async function GET(
  _request: Request,
  { params }: RouteParams
) {
  const { slug } = await params;
  const song = getSongBySlug(slug);

  if (!song) {
    return NextResponse.json(
      { error: 'Song not found' },
      { status: 404 }
    );
  }

  return NextResponse.json(song);
}
