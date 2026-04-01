import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'
import { getResults, connectWebSocket } from '../api'

const stages = [
  { key: 'uploading', label: 'Video Uploaded' },
  { key: 'detecting', label: 'Running Detection (YOLOv8)' },
  { key: 'tracking', label: 'Player Tracking (DeepSORT)' },
  { key: 'analyzing', label: 'Computing Analytics' },
  { key: 'completed', label: 'Analysis Complete' },
]

export default function ProcessingPage() {
  const { matchId } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('processing')
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState(0)

  useEffect(() => {
    const ws = connectWebSocket(matchId, (data) => {
      if (data.type === 'progress') {
        setProgress(data.progress)
        setStatus(data.status)

        if (data.progress < 20) setCurrentStage(1)
        else if (data.progress < 50) setCurrentStage(2)
        else if (data.progress < 80) setCurrentStage(3)
        else if (data.status === 'completed') setCurrentStage(4)
        else setCurrentStage(3)

        if (data.status === 'completed') {
          setTimeout(() => navigate(`/dashboard/${matchId}`), 1500)
        }
      }
    })

    const poll = setInterval(async () => {
      try {
        const result = await getResults(matchId)
        if (result.status === 'completed') {
          setStatus('completed')
          setProgress(100)
          setCurrentStage(4)
          clearInterval(poll)
          setTimeout(() => navigate(`/dashboard/${matchId}`), 1500)
        } else if (result.status === 'failed') {
          setStatus('failed')
          clearInterval(poll)
        } else {
          setProgress(result.progress || 0)
        }
      } catch (e) {}
    }, 3000)

    return () => {
      ws.close()
      clearInterval(poll)
    }
  }, [matchId, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-lg w-full space-y-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Analyzing Match</h1>
          <p className="mt-2 text-white/50 text-sm font-mono">{matchId}</p>
        </div>

        <div className="glass p-8 space-y-6">
          <div className="flex justify-center">
            {status === 'failed' ? (
              <div className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center">
                <XCircle className="w-10 h-10 text-red-400" />
              </div>
            ) : status === 'completed' ? (
              <div className="w-20 h-20 rounded-full bg-green-500/10 flex items-center justify-center">
                <CheckCircle className="w-10 h-10 text-green-400" />
              </div>
            ) : (
              <div className="w-20 h-20 rounded-full bg-accent/10 flex items-center justify-center">
                <Loader2 className="w-10 h-10 text-accent-light animate-spin" />
              </div>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-white/60">Progress</span>
              <span className="font-mono text-accent-light">{Math.round(progress)}%</span>
            </div>
            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-accent to-accent-light rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <div className="space-y-3">
            {stages.map((stage, idx) => (
              <div
                key={stage.key}
                className={`flex items-center gap-3 text-sm transition-all duration-300 ${
                  idx <= currentStage ? 'text-white' : 'text-white/25'
                }`}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                  idx < currentStage
                    ? 'bg-green-500/20 text-green-400'
                    : idx === currentStage
                    ? 'bg-accent/20 text-accent-light'
                    : 'bg-white/5 text-white/20'
                }`}>
                  {idx < currentStage ? (
                    <CheckCircle className="w-3.5 h-3.5" />
                  ) : idx === currentStage && status !== 'failed' ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-current" />
                  )}
                </div>
                {stage.label}
              </div>
            ))}
          </div>
        </div>

        {status === 'failed' && (
          <button
            onClick={() => navigate('/upload')}
            className="w-full btn-secondary"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  )
}
