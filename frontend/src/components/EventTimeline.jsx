import { ArrowRightLeft, Target, ShieldAlert, Clock } from 'lucide-react'

const eventConfig = {
  pass: { icon: ArrowRightLeft, color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Pass' },
  shot: { icon: Target, color: 'text-orange-400', bg: 'bg-orange-500/10', label: 'Shot' },
  tackle: { icon: ShieldAlert, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Tackle' },
  foul: { icon: ShieldAlert, color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Foul' },
}

export default function EventTimeline({ events }) {
  const displayEvents = events.length > 0 ? events.slice(0, 50) : generateDemoEvents()

  return (
    <div className="glass p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
          Match Timeline
        </h3>
        <span className="text-xs text-white/30 font-mono">{displayEvents.length} events</span>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
        {displayEvents.map((event, idx) => {
          const cfg = eventConfig[event.event_type] || eventConfig.pass
          const Icon = cfg.icon
          const mins = Math.floor((event.timestamp || 0) / 60)
          const secs = Math.round((event.timestamp || 0) % 60)

          return (
            <div
              key={idx}
              className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] hover:bg-white/5 transition-colors"
            >
              <div className={`w-8 h-8 rounded-lg ${cfg.bg} flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-4 h-4 ${cfg.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{cfg.label}</p>
                <p className="text-xs text-white/30">
                  {event.player_id !== null && event.player_id !== undefined
                    ? `Player #${event.player_id}`
                    : ''}
                  {event.team_id !== null && event.team_id !== undefined
                    ? ` · Team ${event.team_id === 0 ? 'A' : 'B'}`
                    : ''}
                  {event.metadata?.distance ? ` · ${event.metadata.distance}px` : ''}
                  {event.metadata?.speed ? ` · ${event.metadata.speed} speed` : ''}
                </p>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-white/30 font-mono flex-shrink-0">
                <Clock className="w-3 h-3" />
                {mins}:{secs.toString().padStart(2, '0')}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function generateDemoEvents() {
  const events = []
  const types = ['pass', 'pass', 'pass', 'shot', 'tackle', 'pass', 'pass']
  for (let i = 0; i < 25; i++) {
    events.push({
      event_type: types[i % types.length],
      timestamp: i * 8 + Math.random() * 5,
      player_id: Math.floor(Math.random() * 22) + 1,
      team_id: Math.random() > 0.5 ? 0 : 1,
      metadata: {
        distance: Math.round(30 + Math.random() * 150),
        speed: Math.round(5 + Math.random() * 25),
      },
    })
  }
  return events.sort((a, b) => a.timestamp - b.timestamp)
}
