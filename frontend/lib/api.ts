import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8002/api",
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export interface Genre {
  id: number;
  name: string;
}

export interface MovieBrief {
  id: number;
  tmdb_id: number;
  title: string;
  vote_average: number;
  poster_path: string;
  release_date: string;
  genres: Genre[];
}

export interface MovieFull extends MovieBrief {
  overview: string;
  runtime: number;
  vote_count: number;
  popularity: number;
  backdrop_path: string;
  original_language: string;
  tagline: string;
  director: string;
  top_cast: string;
}

export interface RecommendationItem {
  movie: MovieBrief;
  score: number;
  reason: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// Movies
export const getMovies = (params: {
  page?: number;
  per_page?: number;
  genre?: string;
  search?: string;
  sort_by?: string;
}) => api.get<{ movies: MovieBrief[]; total: number; page: number; per_page: number }>("/movies", { params });

export const getMovie = (id: number) => api.get<MovieFull>(`/movies/${id}`);

export const getTrending = (limit = 20) => api.get<MovieBrief[]>("/movies/trending", { params: { limit } });

export const getGenres = () => api.get<Genre[]>("/movies/genres");

export const getMoviesByGenre = (limit = 15) =>
  api.get<Record<string, MovieBrief[]>>("/movies/by-genre", { params: { limit } });

export const getFeatured = () => api.get<MovieFull[]>("/movies/featured");

// Auth
export const register = (data: { username: string; email: string; password: string }) =>
  api.post<{ id: number; username: string; email: string }>("/users/register", data);

export const login = (data: { username: string; password: string }) =>
  api.post<{ access_token: string; token_type: string }>("/users/login", data);

export const getMe = () => api.get<{ id: number; username: string; email: string }>("/users/me");

// Ratings
export const rateMovie = (movie_id: number, score: number) =>
  api.post("/users/ratings", { movie_id, score });

export const getMyRatings = () => api.get<{ id: number; movie_id: number; score: number }[]>("/users/ratings");

// Recommendations
export const getRecommendations = (top_n = 20) =>
  api.get<{ recommendations: RecommendationItem[]; strategy: string }>("/recommendations", { params: { top_n } });

export const getSimilarMovies = (movieId: number, top_n = 10) =>
  api.get<RecommendationItem[]>(`/recommendations/similar/${movieId}`, { params: { top_n } });

// Chat
export const chatRecommend = (message: string, history: ChatMessage[]) =>
  api.post<{ reply: string; recommended_movies: MovieBrief[] }>("/chat", { message, history });

export default api;
