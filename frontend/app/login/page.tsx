"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await login({ username, password });
      setToken(res.data.access_token);
      router.push("/");
      router.refresh();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20 px-4">
      <h1 className="text-3xl font-bold text-center mb-8">Login</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        <div>
          <label className="block text-sm text-gray-400 mb-1">Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white py-2.5 rounded-lg font-medium transition"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
        <p className="text-center text-gray-400 text-sm">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-amber-500 hover:underline">
            Sign up
          </Link>
        </p>
      </form>
    </div>
  );
}
