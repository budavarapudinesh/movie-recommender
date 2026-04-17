"use client";

import { useEffect, useState } from "react";
import {
  getTrending,
  getMovies,
  getGenres,
  getFeatured,
  getMoviesByGenre,
  type MovieBrief,
  type MovieFull,
  type Genre,
} from "@/lib/api";
import HeroBanner from "@/components/HeroBanner";
import MovieRow from "@/components/MovieRow";
import MovieGrid from "@/components/MovieGrid";

const CONTENT_TYPE_TABS = [
  { label: "All", value: "" },
  { label: "Movies", value: "movie" },
  { label: "Anime", value: "anime" },
  { label: "TV Shows", value: "tv" },
];

export default function Home() {
  const [featured, setFeatured] = useState<MovieFull[]>([]);
  const [genreRows, setGenreRows] = useState<Record<string, MovieBrief[]>>({});
  const [movies, setMovies] = useState<MovieBrief[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [search, setSearch] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("");
  const [selectedContentType, setSelectedContentType] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFeatured()
      .then((res) => setFeatured(res.data))
      .catch((err: unknown) => {
        console.error("Failed to load featured movies:", err);
        getTrending(5)
          .then((res) => {
            setFeatured(res.data as unknown as MovieFull[]);
          })
          .catch((innerErr: unknown) => {
            console.error("Failed to load trending fallback:", innerErr);
          });
      });
    getMoviesByGenre(15)
      .then((res) => setGenreRows(res.data))
      .catch((err: unknown) => {
        console.error("Failed to load genre rows:", err);
      });
    getGenres()
      .then((res) => setGenres(res.data))
      .catch((err: unknown) => {
        console.error("Failed to load genres:", err);
      });
  }, []);

  useEffect(() => {
    setLoading(true);
    getMovies({
      page,
      per_page: 24,
      genre: selectedGenre || undefined,
      search: search || undefined,
      content_type: selectedContentType || undefined,
    })
      .then((res) => {
        setMovies(res.data.movies);
        setTotal(res.data.total);
      })
      .catch((err: unknown) => {
        console.error("Failed to load movies:", err);
        setMovies([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [page, selectedGenre, search, selectedContentType]);

  const totalPages = Math.ceil(total / 24);
  const isFiltering = !!(search || selectedGenre || selectedContentType);
  const genreNames = Object.keys(genreRows);

  const handleContentTypeChange = (value: string) => {
    setSelectedContentType(value);
    setPage(1);
  };

  const handleClearSearch = () => {
    setSearch("");
    setPage(1);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Banner — full viewport width */}
      {!isFiltering && featured.length > 0 && (
        <HeroBanner movies={featured} />
      )}

      {/* Genre Rows (Netflix-style horizontal scrolling) */}
      {!isFiltering && genreNames.length > 0 && (
        <div className="space-y-8 py-10">
          {genreNames.map((genre) => (
            <MovieRow key={genre} title={genre} movies={genreRows[genre]} />
          ))}
        </div>
      )}

      {/* Browse / Discover Section */}
      <div id="discover" className="scroll-mt-0 pb-20">
        <div className="px-4 sm:px-8 lg:px-12 pt-10 pb-4 space-y-5">
          <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-white/40">
            Browse Library
          </h2>

          {/* Content Type Tabs */}
          <div className="flex gap-2 pb-1">
            {CONTENT_TYPE_TABS.map((tab) => (
              <button
                key={tab.value}
                onClick={() => handleContentTypeChange(tab.value)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all border ${
                  selectedContentType === tab.value
                    ? "bg-white text-black border-white shadow-md"
                    : "bg-white/5 text-white/50 border-white/10 hover:bg-white/10 hover:text-white"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Genre Filter Pills */}
          <div className="flex overflow-x-auto gap-2.5 pb-3 scrollbar-hide">
            <button
              onClick={() => { setSelectedGenre(""); setPage(1); }}
              className={`flex-shrink-0 px-5 py-2 rounded-full text-sm font-semibold transition-all border ${
                !selectedGenre
                  ? "bg-white text-black border-white shadow-lg"
                  : "bg-white/5 text-white/50 border-white/10 hover:bg-white/10 hover:text-white"
              }`}
            >
              All Genres
            </button>
            {genres.map((g) => (
              <button
                key={g.id}
                onClick={() => { setSelectedGenre(g.name); setPage(1); }}
                className={`flex-shrink-0 px-5 py-2 rounded-full text-sm font-semibold transition-all border ${
                  selectedGenre === g.name
                    ? "bg-white text-black border-white shadow-lg"
                    : "bg-white/5 text-white/50 border-white/10 hover:bg-white/10 hover:text-white"
                }`}
              >
                {g.name}
              </button>
            ))}
          </div>

          {/* Search Bar */}
          <div className="flex items-center bg-white/5 border border-white/10 rounded-2xl overflow-hidden max-w-xl transition-all focus-within:border-white/30 focus-within:bg-white/8">
            <div className="pl-4 flex items-center text-white/30 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
              </svg>
            </div>
            <input
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search movies, actors, directors..."
              className="flex-1 bg-transparent text-white px-4 py-3 text-sm focus:outline-none placeholder:text-white/25"
            />
            {search && (
              <button
                onClick={handleClearSearch}
                className="pr-4 text-white/30 hover:text-white/60 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 6 6 18" /><path d="m6 6 12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Section Title */}
          {(search || selectedGenre || selectedContentType) && (
            <h3 className="text-lg font-bold text-white">
              {search
                ? `Results for "${search}"`
                : selectedGenre
                ? `${selectedGenre} Movies`
                : CONTENT_TYPE_TABS.find((t) => t.value === selectedContentType)?.label ?? "All"}
            </h3>
          )}
        </div>

        {/* Movie Grid */}
        <div className="px-4 sm:px-8 lg:px-12">
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {Array.from({ length: 24 }).map((_, i) => (
                <div key={i} className="aspect-[2/3] bg-white/5 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : movies.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <div className="text-6xl mb-4 opacity-20">🎬</div>
              <p className="text-xl font-bold text-white/60 mb-2">
                {search ? `No results for "${search}"` : "No movies found"}
              </p>
              <p className="text-sm text-white/30 mb-6">
                Try a different search term or adjust your filters.
              </p>
              {search && (
                <button
                  onClick={handleClearSearch}
                  className="px-6 py-2.5 bg-white/10 border border-white/20 text-white rounded-full text-sm font-medium hover:bg-white/20 transition-colors"
                >
                  Clear search
                </button>
              )}
            </div>
          ) : (
            <MovieGrid
              movies={movies}
              title={!search && !selectedGenre && !selectedContentType ? "All Movies" : ""}
            />
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && !loading && movies.length > 0 && (
          <div className="flex justify-center gap-3 pt-12 px-4">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-5 py-2.5 bg-white/5 border border-white/10 rounded-full disabled:opacity-25 hover:bg-white/10 transition text-sm font-medium flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
              Prev
            </button>
            <span className="px-5 py-2.5 text-white/40 bg-white/5 border border-white/5 rounded-full flex items-center text-sm">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-5 py-2.5 bg-white/5 border border-white/10 rounded-full disabled:opacity-25 hover:bg-white/10 transition text-sm font-medium flex items-center gap-2"
            >
              Next
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6" /></svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
