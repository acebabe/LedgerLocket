import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_BASE || '/api').replace(/\/+$/, '')

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 5000
})

export async function fetchNumbers() {
  const res = await api.get('/numbers')
  return res.data.numbers || []
}

export async function submitTrial({ name, email, numberId }) {
  const res = await api.post('/trial', { name, email, numberId })
  return res.data.trial
}

export async function fetchTrialsAdmin() {
  const res = await api.get('/admin/trials')
  return res.data.trials || []
}

export async function approveTrial(id) {
  const res = await api.post('/admin/approve', { id })
  return res.data.trial
}