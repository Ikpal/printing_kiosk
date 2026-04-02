import { useState, useEffect, useRef } from 'react'
import WelcomeScreen from './screens/WelcomeScreen'
import UploadScreen from './screens/UploadScreen'
import PreviewScreen from './screens/PreviewScreen'
import SettingsScreen from './screens/SettingsScreen'
import PaymentScreen from './screens/PaymentScreen'
import StatusScreen from './screens/StatusScreen'

const IDLE_TIMEOUT_MS = 3 * 60 * 1000;

function App() {
  const [currentScreen, setCurrentScreen] = useState('welcome')
  const [jobId, setJobId] = useState(null)
  const [totalPages, setTotalPages] = useState(0)
  const [thumbnails, setThumbnails] = useState([])
  const [printSettings, setPrintSettings] = useState({
    copies: 1,
    pageRange: 'all',
    colorMode: 'bw',
    duplex: false,
    priceInr: 0,
    printedPages: 0
  })
  
  const timerRef = useRef(null)

  const resetKiosk = () => {
    setCurrentScreen('welcome')
    setJobId(null)
    setTotalPages(0)
    setThumbnails([])
    setPrintSettings({
      copies: 1,
      pageRange: 'all',
      colorMode: 'bw',
      duplex: false,
      priceInr: 0,
      printedPages: 0
    })
  }

  const resetTimer = () => {
    if (timerRef.current) clearTimeout(timerRef.current)
    if (currentScreen !== 'welcome' && currentScreen !== 'status') {
      timerRef.current = setTimeout(resetKiosk, IDLE_TIMEOUT_MS)
    }
  }

  useEffect(() => {
    window.addEventListener('touchstart', resetTimer)
    window.addEventListener('click', resetTimer)
    window.addEventListener('mousemove', resetTimer)
    resetTimer()
    return () => {
      window.removeEventListener('touchstart', resetTimer)
      window.removeEventListener('click', resetTimer)
      window.removeEventListener('mousemove', resetTimer)
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [currentScreen])

  const renderScreen = () => {
    switch(currentScreen) {
      case 'welcome':
        return <WelcomeScreen onStart={() => setCurrentScreen('upload')} />
      case 'upload':
        return <UploadScreen 
                 onUploadSuccess={(id) => { setJobId(id); setCurrentScreen('preview') }} 
                 onCancel={resetKiosk} />
      case 'preview':
        return <PreviewScreen 
                 jobId={jobId} 
                 onLoaded={(pages, thumbs) => { setTotalPages(pages); setThumbnails(thumbs); }}
                 onNext={() => setCurrentScreen('settings')} 
                 onCancel={resetKiosk} 
                 totalPages={totalPages}
                 thumbnails={thumbnails} />
      case 'settings':
        return <SettingsScreen
                 jobId={jobId}
                 totalPages={totalPages}
                 settings={printSettings}
                 updateSettings={setPrintSettings}
                 onNext={() => setCurrentScreen('payment')}
                 onBack={() => setCurrentScreen('preview')}
                 onCancel={resetKiosk} />
      case 'payment':
        return <PaymentScreen
                 jobId={jobId}
                 totalAmount={printSettings.priceInr}
                 onPaymentSuccess={() => setCurrentScreen('status')}
                 onCancel={resetKiosk} />
      case 'status':
        return <StatusScreen
                 jobId={jobId}
                 onComplete={resetKiosk} />
      default:
        return <WelcomeScreen onStart={() => setCurrentScreen('upload')} />
    }
  }

  return (
    <div className="kiosk-container">
      {renderScreen()}
    </div>
  )
}

export default App
