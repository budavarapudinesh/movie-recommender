import Link from "next/link";

export default function NotFound() {
  return (
    <main className="min-h-screen bg-[#0B0B0F] flex items-center justify-center px-4">
      <div className="text-center">
        <div className="text-8xl font-bold text-white/10 mb-4">404</div>
        <h1 className="text-3xl font-bold text-white mb-3">Page Not Found</h1>
        <p className="text-gray-400 mb-8 max-w-md mx-auto">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-[#e50914] text-white rounded-lg hover:bg-[#c4070f] transition-colors font-medium"
        >
          ← Back to Home
        </Link>
      </div>
    </main>
  );
}
