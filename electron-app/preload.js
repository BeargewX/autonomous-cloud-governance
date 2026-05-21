const { contextBridge, shell } = require('electron')
const fs = require('fs')
const path = require('path')

const DEFAULT_CONFIG = {
  baseUrl: 'http://127.0.0.1:5000',
  region: 'ap-southeast-1',
  instanceId: null,
  vpcId: null,
  publicEndpoint: null,
  refreshIntervalMs: 60000,
  apiKey: ''
}

function readJsonIfExists(filePath) {
  if (!fs.existsSync(filePath)) return {}
  return JSON.parse(fs.readFileSync(filePath, 'utf8'))
}

function loadConfig() {
  const configPath = path.join(__dirname, 'config.json')
  const localConfigPath = path.join(__dirname, 'config.local.json')

  const config = {
    ...DEFAULT_CONFIG,
    ...readJsonIfExists(configPath),
    ...readJsonIfExists(localConfigPath)
  }

  if (process.env.DASHBOARD_BASE_URL) {
    config.baseUrl = process.env.DASHBOARD_BASE_URL
  }

  if (process.env.DASHBOARD_API_KEY) {
    config.apiKey = process.env.DASHBOARD_API_KEY
  }

  return config
}

const CONFIG = loadConfig()

async function getJson(apiPath) {
  const headers = {}
  if (CONFIG.apiKey) {
    headers['X-API-Key'] = CONFIG.apiKey
  }

  const res = await fetch(`${CONFIG.baseUrl}${apiPath}`, { headers })

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`)
  }

  return res.json()
}

contextBridge.exposeInMainWorld('api', {
  config: CONFIG,
  baseUrl: CONFIG.baseUrl,
  getCpu: () => getJson('/api/cpu'),
  getIncidents: () => getJson('/api/incidents'),
  getStatus: () => getJson('/api/status'),
  getLambdaStats: () => getJson('/api/lambda-stats'),
  getHealth: () => getJson('/health'),
  getGovernanceScore: () => getJson('/api/governance-score'),
  getPolicyChecks: () => getJson('/api/policy-checks'),
  getDrift: () => getJson('/api/drift'),
  getIncidentPriority: () => getJson('/api/incident-priority'),
  getReport: () => getJson('/api/report'),
  getAssistantSummary: () => getJson('/api/assistant-summary'),
  getCockpitSummary: () => getJson('/api/cockpit-summary'),
  getCostGuard: () => getJson('/api/cost-guard'),
  getSecurityRisks: () => getJson('/api/security-risks'),
  getRunbooks: () => getJson('/api/runbooks'),
  getTopology: () => getJson('/api/topology'),
  getEvidenceReport: () => getJson('/api/evidence-report')
  openExternal: (url) => shell.openExternal(url)
})
