"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b border-transparent ${
        scrolled ? "bg-background/80 backdrop-blur-xl border-white/5 shadow-2xl" : "bg-gradient-to-b from-background/90 to-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex items-center gap-10">
            <Link href="/" className="text-3xl font-heading font-black tracking-tighter uppercase flex items-center gap-1 group">
              <span className="text-accent-primary transition-colors group-hover:text-red-500">AI</span>
              <span className="text-primary-text">REC</span>
            </Link>
            
            <div className="hidden md:flex gap-8 text-sm font-medium">
              <NavLink href="/">Discover</NavLink>
              <NavLink href="/recommendations">AI Picks</NavLink>
              <NavLink href="/chat">Ask AI</NavLink>
              {user && <NavLink href="/#discover">Browse</NavLink>}
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <button className="text-secondary-text hover:text-primary-text transition p-2 hover:bg-white/5 rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </button>
            
            {loading ? null : user ? (
              <div className="flex items-center gap-4">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-sm font-bold text-white shadow-[0_0_15px_rgba(108,99,255,0.4)] border border-white/10 select-none">
                  {user.username[0].toUpperCase()}
                </div>
                <button onClick={logout} className="text-sm font-medium text-secondary-text hover:text-primary-text transition">
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link href="/login" className="text-sm font-medium text-secondary-text hover:text-primary-text transition">Sign In</Link>
                <Link href="/register" className="text-sm font-medium bg-white text-black hover:bg-gray-200 px-6 py-2 rounded-full transition shadow-lg hover:shadow-xl font-bold">
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ href, children }: { href: string, children: React.ReactNode }) {
  return (
    <Link href={href} className="relative text-secondary-text hover:text-primary-text transition duration-300 group py-2 font-medium tracking-wide">
      {children}
      <span className="absolute bottom-0 left-0 w-full h-[2px] bg-white scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300 ease-out" />
    </Link>
  );
}
