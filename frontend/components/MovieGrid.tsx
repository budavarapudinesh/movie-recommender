"use client";

import type { MovieBrief } from "@/lib/api";
import MovieCard from "./MovieCard";

export default function MovieGrid({
  movies,
  title,
}: {
  movies: MovieBrief[];
  title?: string;
}) {
  return (
    <div>
      {title && (
        <h2 className="text-2xl font-bold text-white mb-6">{title}</h2>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </div>
    </div>
  );
}
