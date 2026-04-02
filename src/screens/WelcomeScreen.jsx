import { Printer } from 'lucide-react'

export default function WelcomeScreen({ onStart }) {
  return (
    <div className="screen animate-fade" onClick={onStart}>
      <div className="glass-panel animate-pulse-slow" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '4rem' }}>
        <Printer size={120} color="var(--primary)" style={{ marginBottom: '2rem' }} />
        <h1 className="title">Campus Print</h1>
        <p className="subtitle" style={{ marginBottom: 0 }}>Tap anywhere to start</p>
      </div>
    </div>
  )
}
