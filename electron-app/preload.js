const { contextBridge } = require('electron')

const BASE_URL = 'http://13.228.240.37:5000'

async function getJson(path) {
  const res = await fetch(`${BASE_URL}${path}`)

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`)
  }

  return res.json()
}

contextBridge.exposeInMainWorld('api', {
  baseUrl: BASE_URL,
  getCpu: () => getJson('/api/cpu'),
  getIncidents: () => getJson('/api/incidents'),
  getStatus: () => getJson('/api/status'),
  getLambdaStats: () => getJson('/api/lambda-stats'),
  getHealth: () => getJson('/health')
})
