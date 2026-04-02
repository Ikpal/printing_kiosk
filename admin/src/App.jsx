import { useState, useEffect } from 'react'
import { Printer, FileText, CheckCircle, RefreshCcw, LogOut } from 'lucide-react'

export default function App() {
  const [token, setToken] = useState(sessionStorage.getItem('adminToken'))
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  const [stats, setStats] = useState({ total_jobs: 0, revenue: 0, printer_status: 'online' })
  const [jobs, setJobs] = useState([])
  const [pricing, setPricing] = useState([])

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch('/api/admin/dashboard', { headers: { 'Authorization': 'Basic ' + btoa(`${username}:${password}`) } })
      if (!res.ok) throw new Error("Invalid credentials")
      sessionStorage.setItem('adminToken', btoa(`${username}:${password}`))
      setToken(btoa(`${username}:${password}`))
      setError(null)
    } catch(e) {
      setError(e.message)
    }
  }

  const logout = () => {
    sessionStorage.removeItem('adminToken')
    setToken(null)
  }

  const loadData = async () => {
    if (!token) return
    const headers = { 'Authorization': 'Basic ' + token }
    try {
      const dbRes = await fetch('/api/admin/dashboard', { headers })
      if (dbRes.ok) setStats(await dbRes.json())
      
      const jobsRes = await fetch('/api/admin/jobs', { headers })
      if (jobsRes.ok) setJobs(await jobsRes.json())
      
      const priceRes = await fetch('/api/admin/pricing', { headers })
      if (priceRes.ok) setPricing(await priceRes.json())
    } catch (e) { console.error(e) }
  }

  useEffect(() => {
    if (token) {
      loadData()
      const intv = setInterval(loadData, 10000)
      return () => clearInterval(intv)
    }
  }, [token])

  const handleReprint = async (jobId) => {
    await fetch(`/api/admin/reprint/${jobId}`, { method: 'POST', headers: { 'Authorization': 'Basic ' + token } })
    loadData()
  }

  if (!token) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'var(--bg-dark)' }}>
        <form onSubmit={handleLogin} className="panel" style={{ width: '400px' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Admin Login</h2>
          <div className="grid">
            <input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required />
            <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
            <button type="submit">Login</button>
          </div>
          {error && <p style={{ color: 'var(--danger)', marginTop: '1rem', textAlign: 'center' }}>{error}</p>}
        </form>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Printing Kiosk Admin</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={loadData} style={{ background: 'var(--border)' }}><RefreshCcw size={18} /></button>
          <button onClick={logout} style={{ background: 'var(--danger)' }}><LogOut size={18} /> Logout</button>
        </div>
      </div>

      <div className="grid grid-cols-3" style={{ marginBottom: '2rem' }}>
        <div className="stat-card">
          <div style={{ color: 'var(--text-muted)' }}>Total Jobs</div>
          <div className="stat-value">{stats.total_jobs}</div>
        </div>
        <div className="stat-card">
          <div style={{ color: 'var(--text-muted)' }}>Total Revenue</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>₹{stats.revenue.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div style={{ color: 'var(--text-muted)' }}>Printer Status</div>
          <div className="stat-value" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ width: '16px', height: '16px', borderRadius: '50%', background: stats.printer_status === 'online' ? 'var(--success)' : 'var(--danger)' }}></span>
            {stats.printer_status.toUpperCase()}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2">
        <div className="panel">
          <h2 style={{ marginBottom: '1rem' }}>Recent Jobs</h2>
          <div style={{ overflowX: 'auto', maxHeight: '500px' }}>
            <table>
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Filename</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(j => (
                  <tr key={j.job_id}>
                    <td>{j.job_id.substring(0,8)}...</td>
                    <td>{j.filename}</td>
                    <td>₹{j.amount_inr?.toFixed(2) || '0.00'}</td>
                    <td>
                      <span style={{ 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '4px', 
                        fontSize: '0.85rem',
                        background: j.print_status === 'completed' ? 'var(--success)' : (j.print_status === 'error' ? 'var(--danger)' : 'var(--border)') 
                      }}>
                        {j.print_status}
                      </span>
                    </td>
                    <td>
                      <button onClick={() => handleReprint(j.job_id)} style={{ padding: '0.5rem', fontSize: '0.85rem' }}>Reprint</button>
                    </td>
                  </tr>
                ))}
                {jobs.length === 0 && <tr><td colSpan="5" style={{ textAlign: 'center' }}>No jobs found</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        <div className="panel">
          <h2 style={{ marginBottom: '1rem' }}>Pricing Configuration</h2>
          <table>
            <thead>
              <tr>
                <th>Mode</th>
                <th>Price / Page (₹)</th>
              </tr>
            </thead>
            <tbody>
              {pricing.map(p => (
                <tr key={p.mode}>
                  <td>{p.mode}</td>
                  <td><input type="number" defaultValue={p.price_per_page} step="0.5" style={{ maxWidth: '100px' }} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <button style={{ marginTop: '1.5rem', width: '100%' }}>Save Pricing</button>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '1rem 0 0 0' }}>Note: Update via UI not yet hooked up, but API is ready.</p>
        </div>
      </div>
    </div>
  )
}
