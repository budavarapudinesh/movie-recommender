"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import type { MovieFull } from "@/lib/api";
import { backdropUrl, posterUrl, logoUrl } from "@/lib/tmdb";

export default function HeroBanner({ movies }: { movies: MovieFull[] }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (movies.length <= 1) return;
    const timer = setInterval(() => setCurrent((c) => (c + 1) % movies.length), 8000);
    return () => clearInterval(timer);
  }, [movies.length]);

  if (!movies.length) return null;
  const movie = movies[current];
  const bg = backdropUrl(movie.backdrop_path);
  const poster = posterUrl(movie.poster_path);

  return (
    <div className="relative w-full h-[75vh] min-h-[500px] max-h-[800px] overflow-hidden -mt-16">
      {/* Background image */}
      {bg ? (
        <img
          key={`${movie.id}-backdrop`}
          src={bg}
          alt={movie.title}
          className="absolute inset-0 w-full h-full object-cover animate-[fadeIn_1s_ease-in-out]"
        />
      ) : poster ? (
        <img
          key={`${movie.id}-poster`}
          src={poster}
          alt={movie.title}
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
          <div className="flex items-center gap-3 text-sm flex-wrap">
            <span className="text-green-400 font-bold text-base">{Math.round(movie.vote_average * 10)}% Match</span>
            <span className="text-gray-400">{movie.release_date?.slice(0, 4)}</span>
            {movie.runtime > 0 && (
              <span className="text-gray-400">{Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m</span>
            )}
            {movie.content_type && (
              <span className="text-[11px] font-semibold uppercase tracking-wider bg-white/10 border border-white/15 text-white/70 px-2 py-0.5 rounded-full">
                {movie.content_type === "tv" ? "TV Show" : movie.content_type === "anime" ? "Anime" : "Movie"}
              </span>
            )}
          </div>
          <p className="text-gray-300 text-sm leading-relaxed line-clamp-3 max-w-lg">
            {movie.overview}
          </p>

          {/* Streaming providers in hero */}
          {movie.watch_providers && movie.watch_providers.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-400">Stream on:</span>
              {movie.watch_providers
                .filter((p) => p.type === "flatrate" || p.type === "free")
                .slice(0, 3)
                .map((p) => (
                  <a
                    key={p.provider_id}
                    href={p.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={`Watch on ${p.provider_name}`}
                    className="flex items-center gap-1.5 bg-white/10 hover:bg-white/20 border border-white/10 rounded-md px-2 py-1 transition-all"
                  >
                    {p.logo_path && (
                      <img
                        src={logoUrl(p.logo_path)}
                        alt={p.provider_name}
                        className="w-4 h-4 rounded"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = "none";
                        }}
                      />
                    )}
                    <span className="text-xs text-white/80">{p.provider_name}</span>
                  </a>
                ))}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Link
              href={`/movies/${movie.id}`}
              className="flex items-center gap-2 bg-white text-black font-bold px-6 py-2.5 rounded hover:bg-white/80 transition text-sm"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
              More Info
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-2 bg-gray-500/50 text-white font-bold px-6 py-2.5 rounded hover:bg-gray-500/70 transition text-sm backdrop-blur"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
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
