import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMatches } from '../api'
import { Film, Clock, CheckCircle, Loader2, AlertCircle } from 'lucide-react'

const statusConfig = {
  completed: { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10' },
  processing: { icon: Loader2, color: 'text-accent-light', bg: 'bg-accent/10', spin: true },
  failed: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
  uploaded: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
}

export default function MatchesPage() {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await getMatches()
        setMatches(data)
      } catch (e) {}
      setLoading(false)
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-accent-light animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Match History</h1>
        <Link to="/upload" className="btn-primary text-sm">Upload New</Link>
      </div>

      {matches.length === 0 ? (
        <div className="glass p-12 text-center">
          <Film className="w-12 h-12 text-white/20 mx-auto mb-4" />
          <p className="text-white/40">No matches yet. Upload a video to begin.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {matches.map((match) => {
            const cfg = statusConfig[match.status] || statusConfig.uploaded
            const StatusIcon = cfg.icon
            return (
              <Link
                key={match.match_id}
                to={match.status === 'completed' ? `/dashboard/${match.match_id}` : `/processing/${match.match_id}`}
                className="glass-hover p-5 flex items-center gap-5"
              >
                <div className={`w-10 h-10 rounded-lg ${cfg.bg} flex items-center justify-center`}>
                  <StatusIcon className={`w-5 h-5 ${cfg.color} ${cfg.spin ? 'animate-spin' : ''}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">{match.filename}</p>
                  <p className="text-xs text-white/40 mt-0.5">
                    {match.created_at ? new Date(match.created_at).toLocaleString() : 'Unknown date'}
                    {match.duration_seconds ? ` · ${Math.round(match.duration_seconds)}s` : ''}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-mono px-2.5 py-1 rounded-full ${cfg.bg} ${cfg.color}`}>
                    {match.status}
                  </span>
                  {match.progress > 0 && match.progress < 100 && (
                    <p className="text-xs text-white/30 mt-1">{Math.round(match.progress)}%</p>
                  )}
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
