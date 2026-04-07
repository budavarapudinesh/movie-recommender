"use client";

import { useState, useRef, useEffect } from "react";
import { chatRecommend, type ChatMessage, type MovieBrief } from "@/lib/api";
import MovieCard from "./MovieCard";

const SUGGESTIONS = [
  "Something like Inception but funnier",
  "Best sci-fi films from the 2000s",
  "Underrated action movies with great stories",
  "Romantic comedies that aren't cheesy",
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<(ChatMessage & { movies?: MovieBrief[] })[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;

    const userMsg: ChatMessage = { role: "user", content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await chatRecommend(msg, history);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.reply, movies: res.data.recommended_movies },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 lg:px-12 py-6 space-y-6">
        {/* Empty state with suggestions */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-8 py-12">
            <div>
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600/30 to-purple-700/30 border border-purple-500/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🎬</span>
              </div>
              <h2 className="text-xl font-bold text-white mb-1">Ask me anything about movies</h2>
              <p className="text-secondary-text text-sm max-w-md">
                Get personalized recommendations based on your mood, favorite genres, or specific preferences.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl w-full">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-sm text-white/70 hover:bg-white/10 hover:text-white hover:border-white/20 transition-all"
                >
                  &ldquo;{s}&rdquo;
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message bubbles */}
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center flex-shrink-0 mt-1 shadow-md shadow-purple-900/40">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                  <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z"/>
                  <path d="M8 12h.01M12 12h.01M16 12h.01"/>
                </svg>
              </div>
            )}

            <div className={`max-w-[80%] space-y-4 ${msg.role === "user" ? "items-end flex flex-col" : ""}`}>
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-white text-black font-medium rounded-br-sm"
                    : "bg-white/8 border border-white/10 text-white/90 rounded-bl-sm backdrop-blur-sm"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>

              {/* Recommended movie cards */}
              {msg.movies && msg.movies.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {msg.movies.slice(0, 6).map((m) => (
                    <MovieCard key={m.id} movie={m} size="sm" />
                  ))}
                </div>
              )}
            </div>

            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0 mt-1 text-xs font-bold text-white/70">
                U
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center flex-shrink-0 shadow-md shadow-purple-900/40">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z"/>
                <path d="M8 12h.01M12 12h.01M16 12h.01"/>
              </svg>
            </div>
            <div className="bg-white/8 border border-white/10 rounded-2xl rounded-bl-sm px-5 py-4 backdrop-blur-sm">
              <div className="flex gap-1.5 items-center">
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce [animation-delay:0.15s]" />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce [animation-delay:0.3s]" />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Bar */}
      <div className="flex-shrink-0 border-t border-white/5 px-4 sm:px-8 lg:px-12 py-4">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <div className="flex-1 flex items-center bg-white/5 border border-white/10 rounded-2xl transition-all focus-within:border-white/30 overflow-hidden">
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
              placeholder="Ask for movie recommendations..."
              className="flex-1 bg-transparent text-white px-4 py-3.5 text-sm focus:outline-none placeholder:text-white/25"
              disabled={loading}
            />
          </div>
          <button
            onClick={() => send()}
            disabled={loading || !input.trim()}
            className="flex items-center justify-center w-12 h-12 rounded-2xl bg-white text-black font-bold disabled:opacity-30 hover:bg-white/90 transition-all shadow-lg flex-shrink-0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
