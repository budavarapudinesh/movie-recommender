import type { Metadata } from "next";
import type { ReactNode } from "react";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  try {
    const { id } = await params;
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";
    const res = await fetch(`${baseUrl}/movies/${id}`, { next: { revalidate: 3600 } });
    if (!res.ok) return { title: "Movie | AIREC" };
    const movie = await res.json();
    const poster = movie.poster_path
      ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
      : undefined;
    return {
      title: `${movie.title} | AIREC`,
      description: movie.overview || `Watch ${movie.title} - AI Movie Recommendations`,
      openGraph: {
        title: movie.title,
        description: movie.overview,
        images: poster ? [poster] : [],
      },
    };
  } catch {
    return { title: "Movie | AIREC" };
  }
}

export default function MovieLayout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
