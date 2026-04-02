import { useEffect, useState } from 'react'
import { ArrowRight, XCircle, FileText, Loader2 } from 'lucide-react'

export default function PreviewScreen({ jobId, onLoaded, onNext, onCancel, totalPages, thumbnails }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadPreview() {
      try {
        const res = await fetch(`/api/preview/${jobId}`)
        if (!res.ok) throw new Error("Failed to load preview")
        const data = await res.json()
        onLoaded(data.total_pages, data.thumbnails)
        setLoading(false)
      } catch (e) {
        setError(e.message)
        setLoading(false)
      }
    }
    loadPreview()
  }, [jobId])

  return (
    <div className="screen animate-slide-up">
      <div className="glass-panel" style={{ width: '90%', maxWidth: '1000px', height: '80%' }}>
        <h1 className="title" style={{ fontSize: '3rem', textAlign: 'center' }}>Document Preview</h1>
        
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60%' }}>
            <Loader2 className="animate-spin" size={64} color="var(--primary)" style={{ animation: 'spin 2s linear infinite' }} />
            <h2 style={{ marginTop: '1rem' }}>Generating Preview...</h2>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', marginTop: '4rem' }}>
            <p style={{ color: 'var(--danger)', fontSize: '1.5rem' }}>{error}</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', flex: 1, alignItems: 'center', overflow: 'hidden' }}>
              {thumbnails.map((thumbUrl, idx) => (
                <div key={idx} style={{ flex: 1, maxWidth: '300px', background: 'white', borderRadius: '12px', padding: '0.5rem', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.3)' }}>
                  <img src={`/api${thumbUrl}`} alt={`Page ${idx+1}`} style={{ width: '100%', height: 'auto', borderRadius: '8px' }} />
                  <div style={{ textAlign: 'center', color: '#000', marginTop: '0.5rem', fontWeight: 'bold' }}>Page {idx+1}</div>
                </div>
              ))}
            </div>
            
            <div style={{ textAlign: 'center', margin: '2rem 0' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '1rem', background: 'var(--glass-bg)', padding: '1rem 2rem', borderRadius: '16px' }}>
                <FileText size={32} color="var(--secondary)" />
                <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Total Pages: {totalPages}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: 'auto' }}>
              <button className="btn" onClick={onCancel}>
                <XCircle size={28} /> Cancel
              </button>
              <button className="btn btn-primary" onClick={onNext}>
                Print Settings <ArrowRight size={28} />
              </button>
            </div>
          </div>
        )}
      </div>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
