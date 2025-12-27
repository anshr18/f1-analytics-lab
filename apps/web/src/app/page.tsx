import Link from "next/link";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4">Welcome to F1 Intelligence Hub</h2>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Advanced F1 analytics with ML-powered insights and real-time data
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-12">
        <Link
          href="/dashboard"
          className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-f1red"
        >
          <h3 className="text-2xl font-semibold mb-2">Dashboard</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Explore lap times, stint strategies, and race analysis
          </p>
        </Link>

        <div className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md opacity-50 cursor-not-allowed">
          <h3 className="text-2xl font-semibold mb-2">Predictions</h3>
          <p className="text-gray-600 dark:text-gray-400">Coming in Phase 1: ML predictions</p>
        </div>

        <div className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md opacity-50 cursor-not-allowed">
          <h3 className="text-2xl font-semibold mb-2">Strategy Simulator</h3>
          <p className="text-gray-600 dark:text-gray-400">Coming in Phase 2: Simulate race strategies</p>
        </div>

        <div className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md opacity-50 cursor-not-allowed">
          <h3 className="text-2xl font-semibold mb-2">AI Chat</h3>
          <p className="text-gray-600 dark:text-gray-400">Coming in Phase 3: RAG-powered Q&A</p>
        </div>
      </div>

      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">Phase 0: Data Foundation ✅</h3>
        <ul className="space-y-2 text-gray-700 dark:text-gray-300">
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            FastAPI backend with PostgreSQL + pgvector
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            FastF1 data ingestion pipeline
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            Celery async workers for data processing
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            Next.js 15 frontend with Recharts
          </li>
        </ul>
      </div>
    </div>
  );
}
