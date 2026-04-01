const API_BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || 'API Error')
  }
  return res.json()
}

export async function uploadVideo(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export async function processMatch(matchId) {
  return request(`/process/${matchId}`, { method: 'POST' })
}

export async function getResults(matchId) {
  return request(`/results/${matchId}`)
}

export async function getMetrics(matchId) {
  return request(`/metrics/${matchId}`)
}

export async function getMatches() {
  return request('/matches')
}

export function connectWebSocket(matchId, onMessage) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/match/${matchId}`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch {}
  }

  ws.onopen = () => {
    const keepAlive = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      } else {
        clearInterval(keepAlive)
      }
    }, 30000)
  }

  return ws
}
