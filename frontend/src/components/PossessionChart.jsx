import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function PossessionChart({ data }) {
  const chartData = (data || []).map((d) => ({
    time: `${Math.round(d.timestamp || 0)}s`,
    'Team A': d.team_0 || 50,
    'Team B': d.team_1 || 50,
  }))

  if (chartData.length === 0) {
    chartData.push(
      { time: '0s', 'Team A': 50, 'Team B': 50 },
      { time: '15s', 'Team A': 55, 'Team B': 45 },
      { time: '30s', 'Team A': 48, 'Team B': 52 },
      { time: '45s', 'Team A': 62, 'Team B': 38 },
      { time: '60s', 'Team A': 53, 'Team B': 47 },
    )
  }

  return (
    <div className="glass p-6 space-y-4">
      <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
        Possession Over Time
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="time"
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelStyle={{ color: 'rgba(255,255,255,0.5)' }}
            />
            <Line
              type="monotone"
              dataKey="Team A"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#3b82f6' }}
            />
            <Line
              type="monotone"
              dataKey="Team B"
              stroke="#f97316"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#f97316' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
