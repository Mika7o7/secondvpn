import MatrixRain from '../components/MatrixRain';
import Welcome from '../components/Welcome';
import MainPage from '../components/MainPage';
import LkPage from '../components/LkPage';
import RefPage from '../components/RefPage';
import Navigation from '../components/Navigation';
import '../styles/index.css';

// src/pages/App.tsx
import { useEffect, useState } from 'react'; // ← ДОБАВЬ useEffect

export default function App() {
  const [screen, setScreen] = useState<'welcome' | 'main' | 'lk' | 'ref'>('welcome');

  // СИНХРОНИЗАЦИЯ: hash → screen
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.slice(1);
      if (hash === 'lk' || hash === 'ref' || hash === 'main' || hash === 'welcome') {
        setScreen(hash as any);
      }
    };

    handleHash();
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, []);

  // СИНХРОНИЗАЦИЯ: screen → hash
  useEffect(() => {
    window.location.hash = screen;
  }, [screen]);

  return (
    <>
      <MatrixRain />
      {screen === 'welcome' && <Welcome onClose={() => setScreen('main')} />}
      {screen !== 'welcome' && (
        <>
          <div className="container" style={{ paddingBottom: '100px' }}>
            {screen === 'main' && <MainPage />}
            {screen === 'lk' && <LkPage />}
            {screen === 'ref' && <RefPage />}
          </div>
          <Navigation
            currentPage={screen}
            onNavigate={(page) => {
              if (page === 'main') {
                setScreen('welcome');
              } else {
                setScreen(page as 'lk' | 'ref');
              }
            }}
          />
        </>
      )}
    </>
  );
}