"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getRecommendations, type RecommendationItem } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import MovieCard from "@/components/MovieCard";

export default function RecommendationsPage() {
  const router = useRouter();
  const [recs, setRecs] = useState<RecommendationItem[]>([]);
  const [strategy, setStrategy] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }

    getRecommendations(30)
      .then((res) => {
        setRecs(res.data.recommendations);
        setStrategy(res.data.strategy);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const strategyLabel =
    strategy === "personalized"
      ? "Based on movies you've rated"
      : "Trending movies this week";

  if (loading) {
    return (
      <div className="px-4 sm:px-8 lg:px-12 pt-12 space-y-6">
        <div className="h-8 w-64 bg-white/5 rounded-full animate-pulse" />
        <div className="h-4 w-80 bg-white/5 rounded-full animate-pulse" />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 pt-4">
          {Array.from({ length: 24 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Page Header */}
      <div className="px-4 sm:px-8 lg:px-12 pt-12 pb-8 space-y-2">
        <div className="flex items-center gap-3 mb-1">
          <span className="w-1.5 h-6 bg-accent-primary rounded-full shadow-[0_0_10px_rgba(255,61,90,0.5)]" />
          <h1 className="text-3xl sm:text-4xl font-heading font-black text-white">
            Recommended For You
          </h1>
        </div>
        <p className="text-secondary-text text-sm pl-5">{strategyLabel}</p>
      </div>

      {recs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-32 px-4 text-center">
          <div className="w-24 h-24 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-white/20">
              <path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white mb-2">No recommendations yet</h2>
          <p className="text-secondary-text max-w-md mb-8">
            Rate some movies to help our AI understand your taste and generate personalized picks.
          </p>
          <button
            onClick={() => router.push("/")}
            className="px-8 py-3 bg-white text-black font-bold rounded-full hover:bg-white/90 transition-all shadow-xl"
          >
            Browse Movies
          </button>
        </div>
      ) : (
        <div className="px-4 sm:px-8 lg:px-12 space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
            {recs.map((item) => (
              <div key={item.movie.id} className="space-y-2">
                <MovieCard movie={item.movie} />
                {item.reason && (
                  <p className="text-[11px] text-white/40 line-clamp-2 px-1 leading-relaxed">
                    {item.reason}
                  </p>
                )}
                {/* Match score bar */}
                <div className="flex items-center gap-2 px-1">
                  <div className="flex-1 h-0.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500/70 rounded-full transition-all"
                      style={{ width: `${Math.min(item.score * 100, 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-green-400/70 font-medium flex-shrink-0">
                    {(item.score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
