import { MapPin } from 'lucide-react'

export default function HeatmapPanel({ matchId, heatmapUrl }) {
  return (
    <div className="glass p-6 space-y-4">
      <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
        Player Heatmap
      </h3>

      {heatmapUrl ? (
        <div className="rounded-lg overflow-hidden border border-white/5">
          <img
            src={heatmapUrl}
            alt="Player heatmap"
            className="w-full h-auto"
          />
        </div>
      ) : (
        <div className="relative h-64 rounded-lg overflow-hidden bg-gradient-to-br from-green-900/30 to-green-800/20 border border-white/5">
          <svg viewBox="0 0 105 68" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
            <rect x="0" y="0" width="105" height="68" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />
            <line x1="52.5" y1="0" x2="52.5" y2="68" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />
            <circle cx="52.5" cy="34" r="9.15" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />
            <circle cx="52.5" cy="34" r="0.5" fill="rgba(255,255,255,0.2)" />
            <rect x="0" y="13.85" width="16.5" height="40.3" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />
            <rect x="88.5" y="13.85" width="16.5" height="40.3" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />
            <rect x="0" y="24.85" width="5.5" height="18.3" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />
            <rect x="99.5" y="24.85" width="5.5" height="18.3" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.3" />

            {generateHeatDots().map((dot, i) => (
              <circle
                key={i}
                cx={dot.x}
                cy={dot.y}
                r={dot.r}
                fill={dot.color}
                opacity={dot.opacity}
              />
            ))}
          </svg>
          <div className="absolute bottom-3 left-3 flex items-center gap-1.5 text-xs text-white/30">
            <MapPin className="w-3 h-3" />
            Simulated heatmap (process video for real data)
          </div>
        </div>
      )}
    </div>
  )
}

function generateHeatDots() {
  const dots = []
  const hotspots = [
    { x: 25, y: 34, intensity: 1.0 },
    { x: 52.5, y: 34, intensity: 0.8 },
    { x: 75, y: 34, intensity: 0.7 },
    { x: 35, y: 20, intensity: 0.5 },
    { x: 70, y: 50, intensity: 0.6 },
    { x: 15, y: 34, intensity: 0.4 },
    { x: 90, y: 34, intensity: 0.3 },
  ]

  for (const spot of hotspots) {
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8
      const dist = 3 + Math.random() * 8
      dots.push({
        x: spot.x + Math.cos(angle) * dist,
        y: spot.y + Math.sin(angle) * dist,
        r: 2 + spot.intensity * 3,
        color: spot.intensity > 0.6
          ? 'rgba(239, 68, 68, 0.4)'
          : spot.intensity > 0.3
          ? 'rgba(245, 158, 11, 0.3)'
          : 'rgba(34, 197, 94, 0.2)',
        opacity: 0.3 + spot.intensity * 0.4,
      })
    }
  }
  return dots
}
