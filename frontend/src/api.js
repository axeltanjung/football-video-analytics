const API_BASE = '/api'

export async function uploadVideo(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Upload failed')
  }

  return res.json()
}

export async function startProcessing(matchId) {
  const res = await fetch(`${API_BASE}/process/${matchId}`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to start processing')
  return res.json()
}

export async function getResults(matchId) {
  const res = await fetch(`${API_BASE}/results/${matchId}`)
  if (!res.ok) throw new Error('Failed to fetch results')
  return res.json()
}

export async function getMetrics(matchId) {
  const res = await fetch(`${API_BASE}/metrics/${matchId}`)
  if (!res.ok) throw new Error('Failed to fetch metrics')
  return res.json()
}

export async function getMatches() {
  const res = await fetch(`${API_BASE}/matches`)
  if (!res.ok) throw new Error('Failed to fetch matches')
  return res.json()
}

export function connectWebSocket(matchId, onMessage) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/match/${matchId}`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (e) {
      console.error('WebSocket parse error:', e)
    }
  }

  ws.onopen = () => {
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      } else {
        clearInterval(ping)
      }
    }, 30000)
  }

  return ws
}
