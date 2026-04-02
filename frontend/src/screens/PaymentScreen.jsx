import { useState, useEffect } from 'react'
import { ArrowLeft, XCircle, CheckCircle } from 'lucide-react'

export default function PaymentScreen({ jobId, totalAmount, onPaymentSuccess, onCancel }) {
  const [qrData, setQrData] = useState(null)
  const [txnId, setTxnId] = useState(null)
  const [timeLeft, setTimeLeft] = useState(90)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function initPayment() {
      try {
        const res = await fetch('/api/payment/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_id: jobId })
        })
        if (!res.ok) throw new Error("Could not initialize payment")
        const data = await res.json()
        setQrData(data.qr_data)
        setTxnId(data.txn_id)
      } catch(e) {
        setError(e.message)
      }
    }
    initPayment()
  }, [jobId])

  useEffect(() => {
    if (!txnId) return
    const timer = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timer)
          onCancel()
          return 0
        }
        return t - 1
      })
    }, 1000)

    const poll = setInterval(async () => {
      try {
        const res = await fetch(`/api/payment/status/${txnId}`)
        const data = await res.json()
        if (data.status === 'success') {
          clearInterval(poll)
          clearInterval(timer)
          // Tell backend to trigger print worker
          await fetch(`/api/print/start?job_id=${jobId}`, { method: 'POST' })
          onPaymentSuccess()
        }
      } catch (e) {}
    }, 3000)

    return () => { clearInterval(timer); clearInterval(poll) }
  }, [txnId])

  const simulatePayment = async () => {
    await fetch(`/api/payment/simulate/${txnId}`, { method: 'POST' })
  }

  return (
    <div className="screen animate-slide-up">
      <div className="glass-panel" style={{ width: '80%', maxWidth: '800px', textAlign: 'center' }}>
        <h1 className="title" style={{ fontSize: '3rem' }}>Scan to Pay</h1>
        
        <div style={{ margin: '2rem 0' }}>
          <h2 style={{ fontSize: '4rem', color: 'var(--secondary)', marginBottom: '1rem' }}>₹{totalAmount.toFixed(2)}</h2>
          {qrData ? (
            <div style={{ background: 'white', padding: '2rem', display: 'inline-block', borderRadius: '24px' }}>
              <img src={qrData} alt="UPI QR" style={{ width: '300px', height: '300px' }} />
            </div>
          ) : (
            <p>Generating QR Code...</p>
          )}
        </div>

        <p style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>
          Time remaining: <span style={{ color: timeLeft < 15 ? 'var(--danger)' : 'white' }}>{timeLeft}s</span>
        </p>

        {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: '3rem' }}>
          <button className="btn" onClick={onCancel}>
            <XCircle size={28} /> Cancel
          </button>
          <button className="btn btn-secondary" onClick={simulatePayment}>
            <CheckCircle size={28} /> Simulate Payment
          </button>
        </div>
      </div>
    </div>
  )
}
