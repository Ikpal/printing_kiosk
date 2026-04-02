import { useState, useEffect } from 'react'
import { Loader2, CheckCircle, AlertTriangle } from 'lucide-react'

export default function StatusScreen({ jobId, onComplete }) {
  const [status, setStatus] = useState('queued') // queued, printing, completed, error
  const [errorMsg, setErrorMsg] = useState(null)

  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`/api/print/status/${jobId}`)
        if (!res.ok) return
        const data = await res.json()
        setStatus(data.status)
        if (data.status === 'error') {
          setErrorMsg(data.error)
          clearInterval(poll)
        } else if (data.status === 'completed') {
          clearInterval(poll)
          setTimeout(onComplete, 15000)
        }
      } catch (e) {}
    }, 2000)
    
    return () => clearInterval(poll)
  }, [jobId, onComplete])

  const renderContent = () => {
    if (status === 'completed') {
      return (
        <div style={{ textAlign: 'center' }} className="animate-slide-up">
          <CheckCircle size={120} color="var(--secondary)" style={{ marginBottom: '2rem' }} />
          <h1 className="title">Done!</h1>
          <p className="subtitle">Please collect your printout below.</p>
          <button className="btn btn-secondary" onClick={onComplete} style={{ marginTop: '2rem', marginInline: 'auto' }}>
            Finish
          </button>
        </div>
      )
    }
    if (status === 'error') {
      return (
        <div style={{ textAlign: 'center' }} className="animate-slide-up">
          <AlertTriangle size={120} color="var(--danger)" style={{ marginBottom: '2rem' }} />
          <h1 className="title" style={{ background: 'none', color: 'var(--danger)', WebkitTextFillColor: 'initial' }}>Printer Error</h1>
          <p className="subtitle">{errorMsg || "An unknown error occurred during printing."}</p>
          <button className="btn" onClick={onComplete} style={{ marginTop: '2rem', marginInline: 'auto' }}>
            Start Over
          </button>
        </div>
      )
    }
    
    return (
      <div style={{ textAlign: 'center' }} className="animate-pulse-slow">
        <Loader2 className="animate-spin" size={120} color="var(--primary)" style={{ animation: 'spin 2s linear infinite', marginBottom: '2rem' }} />
        <h1 className="title">
          {status === 'queued' ? 'Queued...' : 'Printing...'}
        </h1>
        <p className="subtitle">Your document is being processed.</p>
      </div>
    )
  }

  return (
    <div className="screen animate-fade">
      <div className="glass-panel" style={{ padding: '6rem 4rem' }}>
        {renderContent()}
      </div>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
