// src/components/RefPage.tsx
export default function RefPage() {
  const copyRefLink = () => {
    navigator.clipboard.writeText('https://matrix-vpn.com/?ref=ABC123');
    alert('Реферальная ссылка скопирована в буфер обмена!');
  };

  return (
    <div className="page active" style={{ textAlign: 'center', padding: '2rem 1rem', minHeight: '100vh' }}>
      
      {/* === MATRIX VPN ЗАГОЛОВОК === */}
      <h1 style={{
        fontSize: 'clamp(2.8rem, 12vw, 5rem)',
        letterSpacing: '0.8rem',
        margin: '0 0 0.5rem 0',
        lineHeight: '1.1',
        fontWeight: 'bold',
      }}>
        MATRIX<br />
      
          VPN
      </h1>

      <div style={{ margin: '3rem auto 2rem', maxWidth: '600px' }}>

        {/* === РЕФЕРАЛЬНАЯ ПРОГРАММА === */}
        <h2 style={{ color: '#0f0', fontSize: '1rem', marginBottom: '1.5rem' }}>
          Реферальная программа
        </h2>

        <div style={{
          background: 'rgba(0, 30, 0, 0.35)',
          border: '1px solid #0f0',
          borderRadius: '14px',
          padding: '2rem 1.5rem',
          marginBottom: '2rem',
          boxShadow: '0 0 30px rgba(0, 255, 0, 0.25)',
        }}>
          <p style={{ fontSize: '0.8rem', marginBottom: '1.2rem', opacity: 0.9 }}>
            Приглашай друзей — и вы оба получите бонусы!
          </p>

          {/* Кликабельная реферальная ссылка */}
          <div
            onClick={copyRefLink}
            style={{
              background: '#000',
              color: '#0f0',
              padding: '12px',
              margin: '1.5rem 0',
              border: '2px solid #0f0',
              borderRadius: '10px',
              fontFamily: 'monospace',
              fontSize: '0.6rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              userSelect: 'all',
              textAlign: 'center',
              boxShadow: '0 0 25px rgba(0, 255, 0, 0.4)',
              transition: 'all 0.3s ease',
              wordBreak: 'break-all',
            }}
            onMouseOver={(e) => e.currentTarget.style.boxShadow = '0 0 40px rgba(0, 255, 0, 0.7)'}
            onMouseOut={(e) => e.currentTarget.style.boxShadow = '0 0 25px rgba(0, 255, 0, 0.4)'}
          >
            https://matrix-vpn.com/?ref=ABC123
          </div>

          <p style={{ fontSize: '0.8rem', margin: '1.5rem 0 0', lineHeight: '1.7' }}>
            Твой друг получит <strong style={{ color: '#0f0' }}>+15 дней</strong> при первой покупке<br />
            А ты — <strong style={{ color: '#0f0' }}>+10 дней</strong> за каждого приглашённого!
          </p>
        </div>

        {/* === КНОПКА ПОДЕЛИТЬСЯ === */}
        <button
          onClick={copyRefLink}
          style={{
            background: 'rgba(0, 255, 0, 0.25)',
            color: '#0f0',
            border: '2px solid #0f0',
            padding: '16px 32px',
            borderRadius: '12px',
            fontWeight: 'bold',
            fontSize: '0.8rem',
            cursor: 'pointer',
            boxShadow: '0 0 25px rgba(0, 255, 0, 0.4)',
            transition: 'all 0.3s ease',
            minWidth: '240px',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(0, 255, 0, 0.4)';
            e.currentTarget.style.boxShadow = '0 0 35px rgba(0, 255, 0, 0.6)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(0, 255, 0, 0.25)';
            e.currentTarget.style.boxShadow = '0 0 25px rgba(0, 255, 0, 0.4)';
          }}
        >
          Скопировать ссылку
        </button>

        <p style={{ marginTop: '2rem', fontSize: '0.8rem', opacity: 0.7 }}>
          Чем больше друзей — тем дольше твой VPN бесплатно
        </p>
      </div>
    </div>
  );
}