# frontend/src/api/client.js
export const API = (import.meta.env.VITE_API_URL || 'http://localhost:5000') + '/api/v1'
const API_KEY = import.meta.env.VITE_TEST_API_KEY || 'change_me'

export async function sendTest(payload){
  const resp = await fetch(API + '/wallets/send-test-coin', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify(payload),
  })
  const data = await resp.json()
  if (!resp.ok) throw new Error(data.error || JSON.stringify(data))
  return data
}

export async function getBalance(address){
  const resp = await fetch(`${API}/ledger/balance?address=${encodeURIComponent(address)}`)
  const data = await resp.json()
  if (!resp.ok) throw new Error(data.error || JSON.stringify(data))
  return data
}
