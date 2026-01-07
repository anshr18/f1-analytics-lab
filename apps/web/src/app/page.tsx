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

        <Link
          href="/predictions"
          className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-f1red"
        >
          <h3 className="text-2xl font-semibold mb-2">Predictions</h3>
          <p className="text-gray-600 dark:text-gray-400">ML-powered predictions for race outcomes</p>
        </Link>

        <Link
          href="/strategy"
          className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow border-2 border-transparent hover:border-f1red"
        >
          <h3 className="text-2xl font-semibold mb-2">Strategy Simulator</h3>
          <p className="text-gray-600 dark:text-gray-400">Calculate undercut/overcut strategies</p>
        </Link>

        <div className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md opacity-50 cursor-not-allowed">
          <h3 className="text-2xl font-semibold mb-2">AI Assistant</h3>
          <p className="text-gray-600 dark:text-gray-400">Coming in Phase 3: RAG-powered Q&A</p>
        </div>
      </div>

      <div className="space-y-4">
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

        <div className="bg-green-50 dark:bg-green-900 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Phase 1: ML Predictions ✅</h3>
          <ul className="space-y-2 text-gray-700 dark:text-gray-300">
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Feature engineering (lap, stint, battle features)
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              4 ML models: Tyre deg, lap time, overtake, race result
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Model training scripts with MinIO storage
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Predictions page with interactive UI
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Dashboard integration with prediction cards
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Async training automation (Celery tasks)
            </li>
          </ul>
        </div>

        <div className="bg-purple-50 dark:bg-purple-900 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Phase 2: Strategy Simulator ✅</h3>
          <ul className="space-y-2 text-gray-700 dark:text-gray-300">
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Undercut/overcut strategy predictor
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Lap-by-lap pit stop simulation
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              ML-powered lap time predictions
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Interactive strategy calculator UI
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Animated charts for gap evolution
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Safety car strategy recommender
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Full race simulation engine with playback
            </li>
          </ul>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Phase 3: AI Assistant 🚀</h3>
          <ul className="space-y-2 text-gray-700 dark:text-gray-300">
            <li className="flex items-center">
              <span className="text-yellow-500 mr-2">○</span>
              RAG-powered question answering
            </li>
            <li className="flex items-center">
              <span className="text-yellow-500 mr-2">○</span>
              Embeddings generation for F1 data
            </li>
            <li className="flex items-center">
              <span className="text-yellow-500 mr-2">○</span>
              Semantic search with pgvector
            </li>
            <li className="flex items-center">
              <span className="text-yellow-500 mr-2">○</span>
              Chat interface with context awareness
            </li>
            <li className="flex items-center">
              <span className="text-yellow-500 mr-2">○</span>
              Natural language query interface
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
