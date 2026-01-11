/**
 * Live Leaderboard Component
 *
 * Real-time F1 race leaderboard with position updates.
 */

import { useEffect, useState } from 'react';
import { Activity, Wifi, WifiOff } from 'lucide-react';
import { useLiveSession, type ConnectionStatus } from '@/hooks/useLiveSession';

interface LeaderboardEntry {
  position: number;
  driver_number: number;
  driver_name?: string;
  gap_to_leader: number | null;
  interval: number | null;
  last_lap_time: number | null;
  sector1_time: number | null;
  sector2_time: number | null;
  sector3_time: number | null;
}

interface LiveLeaderboardProps {
  sessionId: string | null;
  autoConnect?: boolean;
}

/**
 * Format time in seconds to MM:SS.mmm
 */
function formatTime(seconds: number | null): string {
  if (seconds === null) return '-';

  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;

  if (minutes > 0) {
    return `${minutes}:${secs.toFixed(3).padStart(6, '0')}`;
  }
  return secs.toFixed(3);
}

/**
 * Format gap time (e.g., "+12.345")
 */
function formatGap(seconds: number | null): string {
  if (seconds === null || seconds === 0) return '-';
  return `+${seconds.toFixed(3)}`;
}

/**
 * Get status badge styling
 */
function getStatusBadge(status: ConnectionStatus) {
  switch (status) {
    case 'connected':
      return {
        icon: Wifi,
        text: 'LIVE',
        className: 'bg-green-500 text-white',
      };
    case 'connecting':
      return {
        icon: Activity,
        text: 'Connecting...',
        className: 'bg-yellow-500 text-white',
      };
    case 'error':
      return {
        icon: WifiOff,
        text: 'Error',
        className: 'bg-red-500 text-white',
      };
    default:
      return {
        icon: WifiOff,
        text: 'Disconnected',
        className: 'bg-gray-500 text-white',
      };
  }
}

export function LiveLeaderboard({ sessionId, autoConnect = true }: LiveLeaderboardProps) {
  const { status, data, error, connect, disconnect } = useLiveSession({
    sessionId,
    autoConnect,
  });

  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [sessionStatus, setSessionStatus] = useState<string>('Unknown');
  const [currentLap, setCurrentLap] = useState<number>(0);

  // Process live updates
  useEffect(() => {
    if (!data) return;

    // Update leaderboard from timing data
    if (data.data.timing && Array.isArray(data.data.timing)) {
      const entries: LeaderboardEntry[] = data.data.timing
        .map((t: any) => ({
          position: t.position || 0,
          driver_number: t.driver_number || 0,
          gap_to_leader: t.gap_to_leader,
          interval: t.interval,
          last_lap_time: t.last_lap_time,
          sector1_time: t.sector1_time,
          sector2_time: t.sector2_time,
          sector3_time: t.sector3_time,
        }))
        .sort((a: LeaderboardEntry, b: LeaderboardEntry) => a.position - b.position);

      setLeaderboard(entries);

      // Extract current lap from timing data
      const maxLap = Math.max(...entries.map((e) => e.last_lap_time ? 1 : 0));
      if (maxLap > currentLap) {
        setCurrentLap(maxLap);
      }
    }

    // Update session status
    if (data.data.session_status) {
      setSessionStatus(data.data.session_status.status || 'Unknown');
    }
  }, [data, currentLap]);

  const statusBadge = getStatusBadge(status);
  const StatusIcon = statusBadge.icon;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Live Leaderboard</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Lap {currentLap} • {sessionStatus}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Status Badge */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${statusBadge.className}`}>
            <StatusIcon className="w-4 h-4" />
            <span className="text-sm font-semibold">{statusBadge.text}</span>
          </div>

          {/* Connect/Disconnect Button */}
          {sessionId && (
            <button
              onClick={() => (status === 'connected' ? disconnect() : connect())}
              className="px-4 py-2 text-sm font-medium text-white bg-f1red hover:bg-red-700 rounded transition-colors"
            >
              {status === 'connected' ? 'Disconnect' : 'Connect'}
            </button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Leaderboard Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                Pos
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                Driver
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                Gap
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                Interval
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                Last Lap
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                S1
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                S2
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                S3
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {leaderboard.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  {status === 'connected' ? (
                    <div className="flex items-center justify-center gap-2">
                      <Activity className="w-5 h-5 animate-pulse" />
                      <span>Waiting for live data...</span>
                    </div>
                  ) : (
                    'Not connected to live session'
                  )}
                </td>
              </tr>
            ) : (
              leaderboard.map((entry, index) => (
                <tr
                  key={`${entry.driver_number}-${index}`}
                  className="hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                >
                  <td className="px-4 py-3 text-sm font-bold text-gray-900 dark:text-white">
                    {entry.position}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                    #{entry.driver_number}
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600 dark:text-gray-300">
                    {entry.position === 1 ? (
                      <span className="text-green-600 dark:text-green-400 font-semibold">Leader</span>
                    ) : (
                      formatGap(entry.gap_to_leader)
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600 dark:text-gray-300">
                    {formatGap(entry.interval)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right font-mono text-gray-900 dark:text-white">
                    {formatTime(entry.last_lap_time)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right font-mono text-gray-600 dark:text-gray-300">
                    {formatTime(entry.sector1_time)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right font-mono text-gray-600 dark:text-gray-300">
                    {formatTime(entry.sector2_time)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right font-mono text-gray-600 dark:text-gray-300">
                    {formatTime(entry.sector3_time)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-3 bg-gray-50 dark:bg-gray-900">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Data updates in real-time via WebSocket connection • {leaderboard.length} drivers
        </p>
      </div>
    </div>
  );
}
