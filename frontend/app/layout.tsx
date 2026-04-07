import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "MovieRec - AI Movie Recommendations",
  description: "Industry-level hybrid movie recommender powered by ML and Gemini AI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className={`${inter.variable} ${outfit.variable} font-sans bg-background text-primary-text antialiased min-h-screen flex flex-col`}>
        <Navbar />
        <main className="flex-1 w-full pt-16">
          {children}
        </main>
      </body>
    </html>
  );
}
