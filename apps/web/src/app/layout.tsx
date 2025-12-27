import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "F1 Intelligence Hub",
  description: "F1 analytics platform with ML, LLM, and live streaming capabilities",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.Node;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <header className="bg-f1red text-white shadow-lg">
          <div className="container mx-auto px-4 py-4">
            <h1 className="text-2xl font-bold">F1 Intelligence Hub</h1>
            <p className="text-sm opacity-90">Phase 0: Data Foundation</p>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">{children}</main>
        <footer className="mt-16 border-t border-gray-200 dark:border-gray-800 py-8">
          <div className="container mx-auto px-4 text-center text-sm text-gray-600 dark:text-gray-400">
            Built with Next.js, FastAPI, and FastF1
          </div>
        </footer>
      </body>
    </html>
  );
}
