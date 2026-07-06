"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  getMovie,
  getSimilarMovies,
  rateMovie,
  type MovieFull,
  type RecommendationItem,
} from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { posterUrl, backdropUrl } from "@/lib/tmdb";
import RatingStars from "@/components/RatingStars";
import RecommendationCarousel from "@/components/RecommendationCarousel";
import { StreamingProviders } from "@/components/StreamingProviders";

const CONTENT_TYPE_LABELS: Record<string, string> = {
  movie: "Movie",
  tv: "TV Show",
  anime: "Anime",
};

export default function MovieDetailPage() {
  const params = useParams();
  const router = useRouter();
  const movieId = Number(params.id);
  const [movie, setMovie] = useState<MovieFull | null>(null);
  const [similar, setSimilar] = useState<RecommendationItem[]>([]);
  const [userRating, setUserRating] = useState(0);
  const [ratingMsg, setRatingMsg] = useState("");
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    if (!movieId) return;
    getMovie(movieId)
      .then((res) => setMovie(res.data))
      .catch((err: unknown) => {
        console.error("Failed to load movie:", err);
        setLoadError(true);
        router.replace("/not-found");
      });
    getSimilarMovies(movieId)
      .then((res) => setSimilar(res.data))
      .catch((err: unknown) => {
        console.error("Failed to load similar movies:", err);
      });
  }, [movieId, router]);

  const handleRate = async (score: number) => {
    if (!isAuthenticated()) {
      setRatingMsg("Please login to rate movies.");
      return;
    }
    try {
      await rateMovie(movieId, score);
      setUserRating(score);
      setRatingMsg("Rating saved!");
      setTimeout(() => setRatingMsg(""), 2000);
    } catch {
      setRatingMsg("Failed to save rating.");
    }
  };

  const handleWatchlistClick = () => {
    alert("Watchlist coming soon!");
  };

  const handleLikeClick = () => {
    alert("Likes coming soon!");
  };

  if (loadError) {
    return null;
  }

  if (!movie) {
    return (
      <div className="animate-pulse space-y-6 pt-12">
        <div className="h-[60vh] bg-card rounded-xl" />
        <div className="h-8 w-64 bg-card rounded" />
        <div className="h-4 w-full bg-card rounded" />
      </div>
    );
  }

  const year = movie.release_date?.slice(0, 4);
  const hours = Math.floor(movie.runtime / 60);
  const mins = movie.runtime % 60;
  const contentTypeLabel = movie.content_type
    ? (CONTENT_TYPE_LABELS[movie.content_type] ?? movie.content_type)
    : null;
  const justWatchUrl = `https://www.justwatch.com/us/search?q=${encodeURIComponent(movie.title)}`;
  const providers = movie.watch_providers ?? [];

  return (
    <div className="relative -mt-12 -mx-4 sm:-mx-6 lg:-mx-8 min-h-screen pb-20">
      {/* Cinematic Full-bleed Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {movie.backdrop_path ? (
          <>
            <img
              src={backdropUrl(movie.backdrop_path)}
              alt={movie.title}
              className="w-full h-[80vh] object-cover opacity-30 blur-sm scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-r from-background via-black/50 to-transparent" />
          </>
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 to-black" />
        )}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 space-y-16">

        {/* Hero Section */}
        <div className="flex flex-col md:flex-row gap-12 items-start">

          {/* Poster with 3D shadow */}
          <div className="flex-shrink-0 w-full max-w-[300px] mx-auto md:mx-0 perspective-1000">
            {movie.poster_path ? (
              <img
                src={posterUrl(movie.poster_path)}
                alt={movie.title}
                className="w-full rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/10 rotate-y-3 rotate-x-2"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            ) : (
              <div className="w-full aspect-[2/3] bg-card border border-white/5 rounded-2xl flex items-center justify-center text-secondary-text rotate-y-3 rotate-x-2">
                No Poster Available
              </div>
            )}
          </div>

          {/* Info Panel */}
          <div className="flex-1 space-y-6 bg-black/40 backdrop-blur-md p-8 sm:p-10 rounded-3xl border border-white/5 shadow-2xl">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-black tracking-tight drop-shadow-md">
                  {movie.title}
                </h1>
                {contentTypeLabel && (
                  <span className="text-xs font-bold uppercase tracking-widest bg-white/10 border border-white/20 text-white/70 px-3 py-1 rounded-full self-start mt-2">
                    {contentTypeLabel}
                  </span>
                )}
              </div>
              {movie.tagline && (
                <p className="text-accent-secondary font-medium tracking-wide text-lg sm:text-xl drop-shadow-sm">
                  {movie.tagline}
                </p>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-4 text-sm font-medium text-gray-300">
              {year && <span className="bg-white/10 px-2 py-1 rounded">{year}</span>}
              {movie.runtime > 0 && <span>{hours}h {mins}m</span>}
              <div className="flex items-center gap-1.5 bg-green-500/10 border border-green-500/20 text-green-400 px-2 py-1 rounded">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
                <span className="font-bold">{movie.vote_average.toFixed(1)}/10</span>
                <span className="opacity-70 text-xs">({movie.vote_count.toLocaleString()})</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {movie.genres.map((g) => (
                <span
                  key={g.id}
                  className="bg-white/5 border border-white/10 text-white/80 px-4 py-1.5 rounded-full text-sm hover:bg-white/10 transition-colors cursor-default"
                >
                  {g.name}
                </span>
              ))}
            </div>

            <p className="text-secondary-text leading-relaxed text-lg max-w-3xl">
              {movie.overview}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4">
              {movie.director && (
                <div>
                  <h3 className="text-secondary-text text-sm uppercase tracking-wider font-bold mb-1">Director</h3>
                  <p className="text-primary-text font-medium">{movie.director}</p>
                </div>
              )}
              {movie.top_cast && (
                <div>
                  <h3 className="text-secondary-text text-sm uppercase tracking-wider font-bold mb-1">Top Cast</h3>
                  <p className="text-primary-text font-medium">{movie.top_cast}</p>
                </div>
              )}
            </div>

            {/* Streaming Providers — prominent placement */}
            <StreamingProviders
              providers={providers}
              justWatchUrl={justWatchUrl}
            />

            {/* Action Buttons */}
            <div className="pt-6 flex flex-wrap gap-4">
              {movie.trailer_url && (
                <a
                  href={movie.trailer_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 bg-white text-black hover:bg-gray-200 px-8 py-3 rounded-full font-bold transition-transform hover:scale-105 shadow-xl"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  Watch Trailer
                </a>
              )}
              <button
                onClick={handleWatchlistClick}
                className="flex items-center gap-2 bg-card hover:bg-white/10 border border-white/10 text-white px-8 py-3 rounded-full font-bold transition-all shadow-lg hover:border-white/20"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 5v14" /><path d="M5 12h14" />
                </svg>
                Add to Watchlist
              </button>
              <button
                onClick={handleLikeClick}
                className="flex items-center w-12 h-12 justify-center bg-card hover:bg-white/10 border border-white/10 text-white rounded-full font-bold transition-all shadow-lg hover:border-white/20"
                title="Like"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                </svg>
              </button>
            </div>

            {/* AI Rating Interface */}
            <div className="pt-8 mt-8 border-t border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <p className="text-sm font-heading font-bold text-accent-secondary mb-1 uppercase tracking-wider">Help AI Learn Your Taste</p>
                <p className="text-secondary-text text-sm">Rate this movie to improve your recommendations.</p>
              </div>
              <div className="bg-black/50 px-4 py-2 rounded-2xl border border-white/5">
                <RatingStars value={userRating} onChange={handleRate} />
                {ratingMsg && (
                  <p className="text-sm text-accent-primary mt-1 text-center font-medium animate-pulse">
                    {ratingMsg}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Similar Movies Carousel */}
        {similar.length > 0 && (
          <div className="pt-10">
            <h2 className="text-3xl font-heading font-black mb-8 flex items-center gap-3">
              <span className="w-2 h-8 bg-accent-secondary rounded-full shadow-[0_0_10px_rgba(108,99,255,0.8)]"></span>
              Similar Movies
            </h2>
            <RecommendationCarousel items={similar} title="" />
          </div>
        )}
      </div>
    </div>
  );
}
