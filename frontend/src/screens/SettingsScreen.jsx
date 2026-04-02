import { useState, useEffect } from 'react'
import { ArrowLeft, ArrowRight, XCircle, Minus, Plus } from 'lucide-react'

export default function SettingsScreen({ jobId, totalPages, settings, updateSettings, onNext, onBack, onCancel }) {
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState(null)
  
  const updateSetting = (key, value) => {
    updateSettings(prev => ({ ...prev, [key]: value }))
  }

  useEffect(() => {
    async function calculate() {
      setCalculating(true)
      try {
        const res = await fetch('/api/print/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            job_id: jobId,
            copies: settings.copies,
            page_range: settings.pageRange,
            color_mode: settings.colorMode,
            duplex: settings.duplex
          })
        })
        if (!res.ok) throw new Error("Calculation failed")
        const data = await res.json()
        updateSettings(prev => ({ 
          ...prev, 
          priceInr: data.price_inr, 
          printedPages: data.total_pages 
        }))
        setError(null)
      } catch (e) {
        setError("Error calculating price")
      } finally {
        setCalculating(false)
      }
    }
    
    const timeout = setTimeout(calculate, 300)
    return () => clearTimeout(timeout)
  }, [settings.copies, settings.pageRange, settings.colorMode, settings.duplex, jobId])

  return (
    <div className="screen animate-slide-up">
      <div className="glass-panel" style={{ width: '90%', maxWidth: '1000px' }}>
        <h1 className="title" style={{ textAlign: 'center', fontSize: '3rem' }}>Print Settings</h1>
        
        <div className="settings-grid" style={{ marginTop: '2rem' }}>
          
          <div className="setting-card">
            <h3>Copies</h3>
            <div className="control-group">
              <button className="btn btn-secondary btn-icon-large" 
                onClick={() => updateSetting('copies', Math.max(1, settings.copies - 1))}>
                <Minus size={32} />
              </button>
              <span className="value-display">{settings.copies}</span>
              <button className="btn btn-secondary btn-icon-large"
                onClick={() => updateSetting('copies', settings.copies + 1)}>
                <Plus size={32} />
              </button>
            </div>
          </div>

          <div className="setting-card">
            <h3>Color Mode</h3>
            <div className="toggle-group">
              <div className={`toggle-btn ${settings.colorMode === 'bw' ? 'active' : ''}`}
                   onClick={() => updateSetting('colorMode', 'bw')}>
                Black & White
              </div>
              <div className={`toggle-btn ${settings.colorMode === 'color' ? 'active' : ''}`}
                   onClick={() => updateSetting('colorMode', 'color')}>
                Color
              </div>
            </div>
          </div>

          <div className="setting-card">
            <h3>Sides</h3>
            <div className="toggle-group">
              <div className={`toggle-btn ${!settings.duplex ? 'active' : ''}`}
                   onClick={() => updateSetting('duplex', false)}>
                Single-Sided
              </div>
              <div className={`toggle-btn ${settings.duplex ? 'active' : ''}`}
                   onClick={() => updateSetting('duplex', true)}>
                Double-Sided
              </div>
            </div>
          </div>

          <div className="setting-card">
            <h3>Page Range (Optional)</h3>
            <input 
              type="text" 
              value={settings.pageRange}
              onChange={(e) => updateSetting('pageRange', e.target.value)}
              placeholder={`e.g. 1-${totalPages} or all`}
              style={{
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--glass-border)',
                color: 'white',
                padding: '1.5rem',
                fontSize: '1.5rem',
                borderRadius: '16px',
                width: '80%',
                textAlign: 'center',
                outline: 'none'
              }}
            />
            <p style={{ color: 'var(--text-muted)' }}>Currently prints: {settings.printedPages} pages total.</p>
          </div>
          
        </div>

        <div style={{ marginTop: '3rem', textAlign: 'center', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '16px' }}>
          <h2 style={{ fontSize: '2rem' }}>
            Total Cost: <span style={{ color: 'var(--secondary)', fontSize: '3rem', marginLeft: '1rem' }}>₹{settings.priceInr.toFixed(2)}</span>
            {calculating && <span style={{ fontSize: '1rem', marginLeft: '1rem', color: 'var(--text-muted)' }}>(calculating...)</span>}
          </h2>
          {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: '2rem' }}>
          <button className="btn" onClick={onBack}>
            <ArrowLeft size={28} /> Back
          </button>
          <button className="btn" onClick={onCancel}>
            <XCircle size={28} /> Cancel
          </button>
          <button className="btn btn-primary" onClick={onNext} disabled={calculating || error}>
            Proceed to Payment <ArrowRight size={28} />
          </button>
        </div>

      </div>
    </div>
  )
}
