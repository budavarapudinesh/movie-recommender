"use client";

import type { RecommendationItem } from "@/lib/api";
import MovieCard from "./MovieCard";

export default function RecommendationCarousel({
  items,
  title,
}: {
  items: RecommendationItem[];
  title: string;
}) {
  if (!items.length) return null;

  return (
    <div className="mb-8">
      {title && <h2 className="text-xl font-bold text-white mb-4">{title}</h2>}
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-700">
        {items.map((item) => (
          <div key={item.movie.id} className="flex-shrink-0 w-40">
            <MovieCard movie={item.movie} />
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{item.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
