import { useState, useRef, useEffect } from 'react'
import { UploadCloud, XCircle, Smartphone } from 'lucide-react'
import { QRCodeSVG } from 'qrcode.react'

export default function UploadScreen({ onUploadSuccess, onCancel }) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const [qrUrl, setQrUrl] = useState(null)
  const [sessionId, setSessionId] = useState(null)

  useEffect(() => {
    async function initSession() {
      try {
        const res = await fetch('/api/upload/session/new')
        if (res.ok) {
          const data = await res.json()
          setQrUrl(data.url)
          setSessionId(data.session_id)
        }
      } catch (e) {
        console.error("Failed to init mobile session")
      }
    }
    initSession()
  }, [])

  useEffect(() => {
    if (!sessionId) return
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`/api/upload/session/${sessionId}`)
        if (res.ok) {
          const data = await res.json()
          if (data.job_id) {
            clearInterval(poll)
            onUploadSuccess(data.job_id)
          }
        }
      } catch (e) {}
    }, 2000)
    return () => clearInterval(poll)
  }, [sessionId, onUploadSuccess])

  const handleFile = async (file) => {
    if (!file) return
    if (file.size > 20 * 1024 * 1024) {
      setError("File exceeds 20MB limit.")
      return
    }
    
    setUploading(true)
    setError(null)
    
    const progressInterval = setInterval(() => {
      setProgress(p => Math.min(p + 10, 90))
    }, 200)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      
      clearInterval(progressInterval)
      setProgress(100)
      
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Upload failed")
      }
      
      const data = await res.json()
      setTimeout(() => onUploadSuccess(data.job_id), 500)
    } catch (e) {
      setError(e.message)
      setUploading(false)
      setProgress(0)
    }
  }

  return (
    <div className="screen animate-slide-up">
      <div className="glass-panel" style={{ width: '90%', maxWidth: '1000px', textAlign: 'center' }}>
        <h1 className="title" style={{ fontSize: '3rem' }}>Upload Document</h1>
        <p className="subtitle">PDF, DOCX, JPG, PNG (Max 20MB)</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', margin: '2rem 0' }}>
            
            {/* Local Upload */}
            <div 
              style={{ 
                border: '3px dashed var(--glass-border)', 
                borderRadius: '24px', 
                padding: '4rem 2rem',
                cursor: uploading ? 'default' : 'pointer',
                transition: 'all 0.3s'
              }}
              onClick={() => !uploading && fileInputRef.current?.click()}
            >
              {uploading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>Uploading... {progress}%</div>
                  <div style={{ width: '100%', height: '12px', background: 'var(--glass-bg)', borderRadius: '6px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${progress}%`, background: 'var(--primary)', transition: 'width 0.2s' }}></div>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <UploadCloud size={80} color="var(--primary)" style={{ marginBottom: '1rem' }} />
                  <h2>Tap to Select File</h2>
                  <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>From this device</p>
                </div>
              )}
            </div>

            {/* QR Upload */}
            <div style={{ 
                border: '3px solid var(--glass-border)', 
                borderRadius: '24px', 
                padding: '3rem 2rem',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'rgba(0,0,0,0.2)'
            }}>
                <Smartphone size={48} color="var(--secondary)" style={{ marginBottom: '1rem' }} />
                <h2 style={{ marginBottom: '1.5rem' }}>Scan to Upload</h2>
                {qrUrl ? (
                    <div style={{ background: 'white', padding: '1.5rem', borderRadius: '16px' }}>
                        <QRCodeSVG value={qrUrl} size={150} />
                    </div>
                ) : (
                    <p style={{ color: 'var(--text-muted)' }}>Loading QR Code...</p>
                )}
                <p style={{ color: 'var(--text-muted)', marginTop: '1.5rem', fontSize: '1.1rem' }}>Upload seamlessly from your phone!</p>
            </div>
            
        </div>
        
        {error && <p style={{ color: 'var(--danger)', marginTop: '1rem', fontSize: '1.25rem' }}>{error}</p>}
        
        <input 
          type="file" 
          ref={fileInputRef} 
          accept=".pdf,.docx,.jpg,.jpeg,.png"
          onChange={(e) => handleFile(e.target.files[0])} 
          style={{ display: 'none' }}
        />
        
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
          <button className="btn" onClick={onCancel}>
            <XCircle size={28} /> Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
