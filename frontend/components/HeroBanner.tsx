"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import type { MovieFull } from "@/lib/api";

const TMDB_BACKDROP = "https://image.tmdb.org/t/p/original";
const TMDB_IMG = "https://image.tmdb.org/t/p/w500";

export default function HeroBanner({ movies }: { movies: MovieFull[] }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (movies.length <= 1) return;
    const timer = setInterval(() => setCurrent((c) => (c + 1) % movies.length), 8000);
    return () => clearInterval(timer);
  }, [movies.length]);

  if (!movies.length) return null;
  const movie = movies[current];
  const backdropUrl = movie.backdrop_path ? `${TMDB_BACKDROP}${movie.backdrop_path}` : null;
  const posterUrl = movie.poster_path ? `${TMDB_IMG}${movie.poster_path}` : null;

  return (
    <div className="relative w-full h-[75vh] min-h-[500px] max-h-[800px] overflow-hidden -mt-16">
      {/* Background image */}
      {backdropUrl ? (
        <img
          key={movie.id}
          src={backdropUrl}
          alt=""
          className="absolute inset-0 w-full h-full object-cover animate-[fadeIn_1s_ease-in-out]"
        />
      ) : posterUrl ? (
        <img
          key={movie.id}
          src={posterUrl}
          alt=""
          className="absolute inset-0 w-full h-full object-cover blur-2xl scale-110 animate-[fadeIn_1s_ease-in-out]"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 to-black" />
      )}

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/50 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-black/30" />

      {/* Content */}
      <div className="relative z-10 flex items-end h-full pb-24 px-4 sm:px-8 lg:px-12 max-w-[1800px] mx-auto">
        <div className="max-w-xl space-y-4">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white leading-tight drop-shadow-lg">
            {movie.title}
          </h1>
          {movie.tagline && (
            <p className="text-lg text-gray-300 italic">{movie.tagline}</p>
          )}
          <div className="flex items-center gap-3 text-sm">
            <span className="text-green-400 font-bold text-base">{Math.round(movie.vote_average * 10)}% Match</span>
            <span className="text-gray-400">{movie.release_date?.slice(0, 4)}</span>
            {movie.runtime > 0 && (
              <span className="text-gray-400">{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m</span>
            )}
          </div>
          <p className="text-gray-300 text-sm leading-relaxed line-clamp-3 max-w-lg">
            {movie.overview}
          </p>
          <div className="flex gap-3 pt-2">
            <Link
              href={`/movies/${movie.id}`}
              className="flex items-center gap-2 bg-white text-black font-bold px-6 py-2.5 rounded hover:bg-white/80 transition text-sm"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              More Info
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-2 bg-gray-500/50 text-white font-bold px-6 py-2.5 rounded hover:bg-gray-500/70 transition text-sm backdrop-blur"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
              Ask AI
            </Link>
          </div>
        </div>
      </div>

      {/* Slide indicators */}
      {movies.length > 1 && (
        <div className="absolute bottom-8 right-8 flex gap-1.5 z-20">
          {movies.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              className={`h-0.5 rounded-full transition-all duration-500 ${
                i === current ? "w-8 bg-white" : "w-4 bg-white/30"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
