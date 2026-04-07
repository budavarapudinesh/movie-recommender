"use client";

import Link from "next/link";
import type { MovieBrief } from "@/lib/api";

const TMDB_IMG = "https://image.tmdb.org/t/p/w500";

const GENRE_GRADIENTS: Record<string, string> = {
  Action: "from-red-900 to-orange-800",
  Adventure: "from-emerald-900 to-teal-800",
  Animation: "from-sky-800 to-indigo-900",
  Comedy: "from-yellow-800 to-amber-900",
  Crime: "from-gray-900 to-slate-800",
  Drama: "from-purple-900 to-indigo-800",
  Family: "from-pink-800 to-rose-900",
  Fantasy: "from-violet-900 to-purple-800",
  Horror: "from-gray-950 to-red-950",
  Romance: "from-rose-900 to-pink-800",
  "Science Fiction": "from-cyan-900 to-blue-900",
  Thriller: "from-zinc-900 to-neutral-800",
};

function getGradient(genres: { name: string }[]): string {
  for (const g of genres) {
    if (GENRE_GRADIENTS[g.name]) return GENRE_GRADIENTS[g.name];
  }
  return "from-gray-800 to-gray-900";
}

export default function MovieCard({ movie, size = "md" }: { movie: MovieBrief; size?: "sm" | "md" | "lg" }) {
  const year = movie.release_date?.slice(0, 4) || "";
  const posterUrl = movie.poster_path ? `${TMDB_IMG}${movie.poster_path}` : null;
  const widthClass = size === "sm" ? "w-32" : size === "lg" ? "w-56" : "w-44";

  return (
    <Link href={`/movies/${movie.id}`} className={`group block flex-shrink-0 ${widthClass} perspective-1000`}>
      <div className="relative aspect-[2/3] rounded-2xl overflow-hidden bg-card border border-white/5 shadow-lg transform-gpu transition-all duration-500 ease-out 
                      group-hover:-translate-y-1.5 group-hover:shadow-2xl group-hover:border-white/20
                      hover:-rotate-y-1 hover:rotate-x-2">
        
        {/* Poster Image */}
        {posterUrl ? (
          <img
            src={posterUrl}
            alt={movie.title}
            className="w-full h-full object-cover rounded-2xl transition-transform duration-700 ease-in-out group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${getGradient(movie.genres)} flex flex-col items-center justify-center p-3`}>
            <span className="text-3xl font-heading font-bold text-white/70 mb-1">
              {movie.title.split(" ").map(w => w[0]).join("").slice(0, 3)}
            </span>
            <span className="text-[10px] text-white/40 text-center line-clamp-2">{movie.title}</span>
          </div>
        )}

        {/* Cinematic Dark Overlay on Hover */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
          <p className="text-white text-sm font-heading font-bold leading-tight mb-1 line-clamp-1">{movie.title}</p>
          
          <div className="flex items-center gap-2 text-[10px] font-medium mb-2 opacity-80">
            <span className="text-green-400 border border-green-500/30 bg-green-500/10 px-1 rounded">{Math.round(movie.vote_average * 10)}% Match</span>
            <span className="text-gray-300">{year}</span>
          </div>
          
          <div className="flex gap-1 mb-3 flex-wrap">
            {movie.genres.slice(0, 2).map((g) => (
              <span key={g.id} className="text-[9px] text-white/70 bg-white/10 px-1.5 py-0.5 rounded-full border border-white/5 backdrop-blur-md">
                {g.name}
              </span>
            ))}
          </div>

          <div className="flex gap-2">
            <button className="flex-1 bg-white hover:bg-gray-200 text-black text-xs font-bold py-1.5 rounded-full transition-colors flex items-center justify-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
              Play
            </button>
            <button className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md flex items-center justify-center text-white transition-colors" title="Add to Watchlist">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
            </button>
          </div>
        </div>

        {/* Floating Rating Badge */}
        <div className="absolute top-2 right-2 bg-black/40 backdrop-blur-md text-white border border-white/10 text-[11px] font-bold px-2 py-1 rounded-full shadow-lg">
          ⭐ {movie.vote_average.toFixed(1)}
        </div>
      </div>
    </Link>
  );
}
