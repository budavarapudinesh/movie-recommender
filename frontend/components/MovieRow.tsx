"use client";

import { useRef, useState } from "react";
import type { MovieBrief } from "@/lib/api";
import MovieCard from "./MovieCard";

export default function MovieRow({ title, movies }: { title: string; movies: MovieBrief[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 10);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 10);
  };

  const scroll = (dir: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const distance = el.clientWidth * 0.8;
    el.scrollBy({ left: dir === "left" ? -distance : distance, behavior: "smooth" });
  };

  if (!movies.length) return null;

  return (
    <div className="relative group/row">
      <h2 className="text-lg sm:text-xl font-bold text-white mb-3 px-4 sm:px-8 lg:px-12">
        {title}
      </h2>
      <div className="relative">
        {/* Left arrow */}
        {canScrollLeft && (
          <button
            onClick={() => scroll("left")}
            className="absolute left-0 top-0 bottom-0 z-20 w-12 bg-gradient-to-r from-black/80 to-transparent flex items-center justify-center opacity-0 group-hover/row:opacity-100 transition-opacity"
          >
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
              <path d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}

        {/* Scrollable row */}
        <div
          ref={scrollRef}
          onScroll={checkScroll}
          className="flex gap-2 overflow-x-auto scrollbar-hide px-4 sm:px-8 lg:px-12 pb-2"
        >
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>

        {/* Right arrow */}
        {canScrollRight && (
          <button
            onClick={() => scroll("right")}
            className="absolute right-0 top-0 bottom-0 z-20 w-12 bg-gradient-to-l from-black/80 to-transparent flex items-center justify-center opacity-0 group-hover/row:opacity-100 transition-opacity"
          >
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
              <path d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
