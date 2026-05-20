const { contextBridge } = require('electron')

const BASE_URL = 'http://13.228.240.37:5000'

contextBridge.exposeInMainWorld('api', {
  getCpu: async () => {
    const res = await fetch(`${BASE_URL}/api/cpu`)
    return res.json()
  },
  getIncidents: async () => {
    const res = await fetch(`${BASE_URL}/api/incidents`)
    return res.json()
  },
  getStatus: async () => {
    const res = await fetch(`${BASE_URL}/api/status`)
    return res.json()
  },
  getLambdaStats: async () => {
    const res = await fetch(`${BASE_URL}/api/lambda-stats`)
    return res.json()
  },
  getHealth: async () => {
    const res = await fetch(`${BASE_URL}/health`)
    return res.json()
  }
})