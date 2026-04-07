"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex items-center gap-4 px-4 sm:px-8 lg:px-12 pt-8 pb-4 border-b border-white/5 flex-shrink-0">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg shadow-purple-900/40">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
            <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z"/>
            <path d="M8 12h.01M12 12h.01M16 12h.01"/>
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-heading font-bold text-white leading-none">AI Movie Assistant</h1>
          <p className="text-xs text-secondary-text mt-0.5">Powered by Gemini AI</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-green-400 font-medium">Online</span>
        </div>
      </div>

      {/* Chat Interface */}
      <ChatInterface />
    </div>
  );
}
