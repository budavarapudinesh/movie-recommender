const TMDB_BASE = process.env.NEXT_PUBLIC_TMDB_IMAGE_BASE ?? "https://image.tmdb.org/t/p";

export function posterUrl(
  path: string,
  size: "w200" | "w300" | "w500" | "original" = "w500"
): string {
  if (!path) return "";
  return `${TMDB_BASE}/${size}${path}`;
}

export function backdropUrl(
  path: string,
  size: "w780" | "w1280" | "original" = "w1280"
): string {
  if (!path) return "";
  return `${TMDB_BASE}/${size}${path}`;
}

export function logoUrl(path: string): string {
  if (!path) return "";
  return `${TMDB_BASE}/w45${path}`;
}
