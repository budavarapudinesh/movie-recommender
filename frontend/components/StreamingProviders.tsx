"use client";

import { WatchProvider } from "@/lib/api";
import { logoUrl } from "@/lib/tmdb";

interface StreamingProvidersProps {
  providers: WatchProvider[];
  movieTitle: string;
  justWatchUrl: string;
}

export function StreamingProviders({ providers, movieTitle, justWatchUrl }: StreamingProvidersProps) {
  const streamProviders = providers.filter(
    (p) => p.type === "flatrate" || p.type === "free" || p.type === "ads"
  );
  const rentProviders = providers.filter(
    (p) => p.type === "rent" || p.type === "buy"
  );

  if (providers.length === 0) {
    return (
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Where to Watch
        </h3>
        <a
          href={justWatchUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 bg-[#1a1a2e] border border-[#e8b43a] text-[#e8b43a] rounded-lg hover:bg-[#e8b43a] hover:text-black transition-colors text-sm font-medium"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
          </svg>
          Find on JustWatch
        </a>
      </div>
    );
  }

  return (
    <div className="mt-6 space-y-4">
      {streamProviders.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Stream
          </h3>
          <div className="flex flex-wrap gap-3">
            {streamProviders.map((p) => (
              <a
                key={p.provider_id}
                href={p.link}
                target="_blank"
                rel="noopener noreferrer"
                title={`Watch on ${p.provider_name}`}
                className="flex items-center gap-2 px-3 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-all group border border-white/5"
              >
                {p.logo_path && (
                  <img
                    src={logoUrl(p.logo_path)}
                    alt={p.provider_name}
                    className="w-6 h-6 rounded"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                )}
                <span className="text-sm font-medium text-white group-hover:text-white">
                  {p.provider_name}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}

      {rentProviders.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Rent / Buy
          </h3>
          <div className="flex flex-wrap gap-3">
            {rentProviders.map((p) => (
              <a
                key={p.provider_id}
                href={p.link}
                target="_blank"
                rel="noopener noreferrer"
                title={`${p.type === "rent" ? "Rent" : "Buy"} on ${p.provider_name}`}
                className="flex items-center gap-2 px-3 py-2 bg-white/5 rounded-lg hover:bg-white/15 transition-all border border-white/10"
              >
                {p.logo_path && (
                  <img
                    src={logoUrl(p.logo_path)}
                    alt={p.provider_name}
                    className="w-5 h-5 rounded"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                )}
                <span className="text-sm text-gray-300">
                  {p.type === "rent" ? "Rent" : "Buy"} on {p.provider_name}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}

      <a
        href={justWatchUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-[#e8b43a] transition-colors"
      >
        Powered by JustWatch ↗
      </a>
    </div>
  );
}
