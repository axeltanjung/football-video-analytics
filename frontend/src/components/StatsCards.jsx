import { Users, Target, ArrowRightLeft, Timer } from 'lucide-react'

export default function StatsCards({ metrics }) {
  if (!metrics) return null

  const possession = metrics.possession || {}
  const team0 = possession['0'] || possession[0] || 0
  const team1 = possession['1'] || possession[1] || 0

  const passes = metrics.passes || metrics.total_passes || {}
  const totalPasses = Object.values(passes).reduce((a, b) => a + b, 0)

  const shots = metrics.shots || {}
  const totalShots = Object.values(shots).reduce((a, b) => a + b, 0)

  const shotsOnTarget = metrics.shots_on_target || {}
  const totalOnTarget = Object.values(shotsOnTarget).reduce((a, b) => a + b, 0)

  const duration = metrics.duration_seconds || 0
  const mins = Math.floor(duration / 60)
  const secs = Math.round(duration % 60)

  const cards = [
    {
      label: 'Possession',
      value: `${team0}% – ${team1}%`,
      sub: 'Team A vs Team B',
      icon: Users,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      bar: { a: team0, b: team1 },
    },
    {
      label: 'Total Passes',
      value: totalPasses.toString(),
      sub: `Accuracy: ${Object.values(metrics.pass_accuracy || {}).map(v => `${v}%`).join(' / ') || 'N/A'}`,
      icon: ArrowRightLeft,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
    },
    {
      label: 'Shots',
      value: `${totalShots}`,
      sub: `${totalOnTarget} on target`,
      icon: Target,
      color: 'text-orange-400',
      bg: 'bg-orange-500/10',
    },
    {
      label: 'Duration',
      value: `${mins}:${secs.toString().padStart(2, '0')}`,
      sub: `${metrics.total_frames || 0} frames processed`,
      icon: Timer,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <div key={card.label} className="stat-card space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-white/40 uppercase tracking-wider">
                {card.label}
              </span>
              <div className={`w-8 h-8 rounded-lg ${card.bg} flex items-center justify-center`}>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
            </div>
            <p className="text-2xl font-bold tracking-tight">{card.value}</p>
            {card.bar && (
              <div className="flex h-1.5 rounded-full overflow-hidden bg-white/5">
                <div
                  className="bg-blue-500 rounded-l-full"
                  style={{ width: `${card.bar.a}%` }}
                />
                <div
                  className="bg-orange-500 rounded-r-full"
                  style={{ width: `${card.bar.b}%` }}
                />
              </div>
            )}
            <p className="text-xs text-white/30">{card.sub}</p>
          </div>
        )
      })}
    </div>
  )
}
