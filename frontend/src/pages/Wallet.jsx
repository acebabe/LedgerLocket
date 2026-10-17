# frontend/src/pages/Wallet.jsx
import React, { useState } from 'react'
import { sendTest, getBalance } from '../api/client'

export default function Wallet(){
  const [to, setTo] = useState('')
  const [recipientEmail, setRecipientEmail] = useState('')
  const [amount, setAmount] = useState('0.01')
  const [status, setStatus] = useState(null)
  const [balance, setBalance] = useState(null)

  async function onSend(e){
    e.preventDefault()
    setStatus('sending...')
    try{
      const res = await sendTest({ to, amount, chain_id: 11155111, recipient_email: recipientEmail, note: 'test credit' })
      setStatus('sent: ' + (res.tx_hash || res.status))
      if (to) {
        const b = await getBalance(to)
        setBalance(b)
      }
    } catch (err) {
      setStatus('error: ' + (err.message || JSON.stringify(err)))
    }
  }

  return (
    <div>
      <h2>Send Test Credit</h2>
      <form onSubmit={onSend}>
        <div>
          <label>To wallet address</label><br/>
          <input value={to} onChange={e => setTo(e.target.value)} style={{width:'100%'}} />
        </div>
        <div>
          <label>Recipient email (optional, for alert)</label><br/>
          <input value={recipientEmail} onChange={e => setRecipientEmail(e.target.value)} style={{width:'100%'}} />
        </div>
        <div>
          <label>Amount (ETH)</label><br/>
          <input value={amount} onChange={e => setAmount(e.target.value)} />
        </div>
        <button type="submit">Send</button>
      </form>
      {status && <p>{status}</p>}
      {balance && (
        <div style={{marginTop:20, border:'1px solid #ddd', padding:12}}>
          <h3>Off-chain balance</h3>
          <p>Address: {balance.address}</p>
          <p>Balance: {balance.balance}</p>
          <p>Locked: {balance.locked}</p>
        </div>
      )}
    </div>
  )
}
