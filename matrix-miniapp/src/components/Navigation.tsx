// src/components/Navigation.tsx
import { Home, User, Users } from 'lucide-react';

type Props = {
  currentPage: string;
  onNavigate: (page: string) => void;
};

export default function Navigation({ currentPage, onNavigate }: Props) {
  // Главная активна на welcome И на main
  const isHomeActive = currentPage === 'welcome' || currentPage === 'main';
  const isLkActive = currentPage === 'lk';
  const isRefActive = currentPage === 'ref';

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '18px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '85%',                    // уже!
        maxWidth: '380px',               // ещё уже!
        background: 'rgba(0, 30, 0, 0.45)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        border: '1px solid rgba(0, 255, 0, 0.35)',
        borderRadius: '22px',
        padding: '10px 12px',
        zIndex: 100,
        boxShadow: '0 10px 35px rgba(0, 255, 0, 0.2)',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          gap: '10px',
        }}
      >
        {/* Главная */}
        <button
          onClick={() => onNavigate('main')}
          style={{
            flex: 1,
            background: isHomeActive ? 'rgba(0, 255, 0, 0.3)' : 'transparent',
            color: isHomeActive ? '#0f0' : '#0a8',
            border: 'none',
            borderRadius: '16px',
            padding: '10px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: isHomeActive ? '0 0 22px rgba(0, 255, 0, 0.5)' : 'none',
            opacity: isHomeActive ? 1 : 0.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseOver={(e) => !isHomeActive && (e.currentTarget.style.opacity = '0.85')}
          onMouseOut={(e) => !isHomeActive && (e.currentTarget.style.opacity = '0.5')}
        >
          <Home size={14} strokeWidth={2.8} />
        </button>

        {/* ЛК */}
        <button
          onClick={() => onNavigate('lk')}
          style={{
            flex: 1,
            background: isLkActive ? 'rgba(0, 255, 0, 0.3)' : 'transparent',
            color: isLkActive ? '#0f0' : '#0a8',
            border: 'none',
            borderRadius: '16px',
            padding: '10px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: isLkActive ? '0 0 22px rgba(0, 255, 0, 0.5)' : 'none',
            opacity: isLkActive ? 1 : 0.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseOver={(e) => !isLkActive && (e.currentTarget.style.opacity = '0.85')}
          onMouseOut={(e) => !isLkActive && (e.currentTarget.style.opacity = '0.5')}
        >
          <User size={14} strokeWidth={2.8} />
        </button>

        {/* Рефералы */}
        <button
          onClick={() => onNavigate('ref')}
          style={{
            flex: 1,
            background: isRefActive ? 'rgba(0, 255, 0, 0.3)' : 'transparent',
            color: isRefActive ? '#0f0' : '#0a8',
            border: 'none',
            borderRadius: '16px',
            padding: '10px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: isRefActive ? '0 0 22px rgba(0, 255, 0, 0.5)' : 'none',
            opacity: isRefActive ? 1 : 0.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseOver={(e) => !isRefActive && (e.currentTarget.style.opacity = '0.85')}
          onMouseOut={(e) => !isRefActive && (e.currentTarget.style.opacity = '0.5')}
        >
          <Users size={14} strokeWidth={2.8} />
        </button>
      </div>
    </div>
  );
}