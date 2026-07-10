import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Self-Healing RAG Pipeline | Dashboard",
  description:
    "Real-time observability dashboard for an autonomous self-healing RAG pipeline with agentic error correction.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased">
      <body className="min-h-screen bg-surface-950 text-surface-50">
        {children}
      </body>
    </html>
  );
}
