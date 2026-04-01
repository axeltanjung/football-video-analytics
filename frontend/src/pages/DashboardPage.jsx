import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getResults, getMetrics } from '../api'
import StatsCards from '../components/StatsCards'
import PossessionChart from '../components/PossessionChart'
import PassDistribution from '../components/PassDistribution'
import HeatmapPanel from '../components/HeatmapPanel'
import EventTimeline from '../components/EventTimeline'
import { Loader2 } from 'lucide-react'
import { DEMO_ANALYTICS, DEMO_METRICS } from '../demoData'

export default function DashboardPage() {
  const { matchId } = useParams()
  const [analytics, setAnalytics] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [useDemo, setUseDemo] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const [res, met] = await Promise.all([
          getResults(matchId),
          getMetrics(matchId),
        ])
        if (res.analytics && Object.keys(res.analytics).length > 0) {
          setAnalytics(res)
          setMetrics(met)
        } else {
          setUseDemo(true)
          setAnalytics(DEMO_ANALYTICS)
          setMetrics(DEMO_METRICS)
        }
      } catch (e) {
        setUseDemo(true)
        setAnalytics(DEMO_ANALYTICS)
        setMetrics(DEMO_METRICS)
      }
      setLoading(false)
    }
    load()
  }, [matchId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-accent-light animate-spin" />
      </div>
    )
  }

  const data = useDemo ? DEMO_ANALYTICS : analytics
  const met = useDemo ? DEMO_METRICS : metrics

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Match Dashboard</h1>
          <p className="text-white/40 text-sm font-mono mt-1">
            {useDemo ? 'Demo Data' : matchId}
          </p>
        </div>
        {useDemo && (
          <span className="text-xs font-mono px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
            SAMPLE DATA
          </span>
        )}
      </div>

      <StatsCards metrics={met} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PossessionChart data={met?.possession_timeline || data?.analytics?.possession_timeline || []} />
        <PassDistribution metrics={met} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HeatmapPanel matchId={matchId} heatmapUrl={data?.heatmap_url} />
        <EventTimeline events={data?.events || data?.analytics?.events || []} />
      </div>
    </div>
  )
}
