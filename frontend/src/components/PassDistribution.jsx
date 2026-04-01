import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'

export default function PassDistribution({ metrics }) {
  if (!metrics) return null

  const passes = metrics.passes || metrics.total_passes || {}
  const accuracy = metrics.pass_accuracy || {}
  const shots = metrics.shots || {}
  const shotsOnTarget = metrics.shots_on_target || {}

  const data = [
    {
      name: 'Passes A',
      value: passes['0'] || passes[0] || 0,
      color: '#3b82f6',
    },
    {
      name: 'Passes B',
      value: passes['1'] || passes[1] || 0,
      color: '#f97316',
    },
    {
      name: 'Accuracy A',
      value: accuracy['0'] || accuracy[0] || 0,
      color: '#22c55e',
    },
    {
      name: 'Accuracy B',
      value: accuracy['1'] || accuracy[1] || 0,
      color: '#eab308',
    },
    {
      name: 'Shots A',
      value: shots['0'] || shots[0] || 0,
      color: '#8b5cf6',
    },
    {
      name: 'Shots B',
      value: shots['1'] || shots[1] || 0,
      color: '#ec4899',
    },
  ]

  return (
    <div className="glass p-6 space-y-4">
      <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider">
        Pass & Shot Distribution
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barSize={32}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="name"
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            />
            <YAxis
              tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {data.map((entry, idx) => (
                <Cell key={idx} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
