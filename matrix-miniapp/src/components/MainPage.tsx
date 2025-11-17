// src/pages/MainPage.tsx — ЧИСТЕЙШИЙ КОД 2025 ГОДА
import { useEffect, useState } from 'react';
import { api } from '../api';

export default function MainPage() {
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 1628997906;
  const [key, setKey] = useState<string>("Ключ генерируется...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMyData(userId)
      .then(data => {
        // Бэкенд уже всё сделал: создал пользователя и триал, если нужно
        const trialKey = data.keys.find((k: any) => k.is_trial);
        const anyKey = trialKey || data.keys[0];
        setKey(anyKey?.key || "Ключ недоступен");
      })
      .catch(() => {
        setKey("Ошибка загрузки");
      })
      .finally(() => setLoading(false));
  }, [userId]);

  const copyKey = () => {
    if (key && key.includes('vless://')) {
      navigator.clipboard.writeText(key);
      alert('Ключ скопирован!');
    }
  };

  if (loading) {
    return <div style={{color: '#0f0', textAlign: 'center', padding: '4rem'}}>
      Получаем твой ключ...
    </div>;
  }

  return (
    <div className="page active" style={{ textAlign: 'center', padding: '2rem 1rem' }}>
      <h1 style={{fontSize: 'clamp(2.8rem, 12vw, 5rem)', letterSpacing: '0.8rem', margin: '0 0 0.5rem', fontWeight: 'bold'}}>
        MATRIX<br />VPN
      </h1>

      <div style={{ margin: '3rem auto 2rem', maxWidth: '600px' }}>
        <h2 style={{ color: '#0f0', fontSize: '1.6rem', marginBottom: '1.5rem' }}>
          Как подключиться
        </h2>
        <div style={{
          textAlign: 'left', background: 'rgba(0,30,0,0.3)', padding: '1.5rem',
          borderRadius: '8px', border: '1px solid #0f0', fontSize: '0.7rem', lineHeight: '1.8'
        }}>
          <p><strong>2.</strong> Скопируйте ключ одним кликом:</p>
          <div
            onClick={copyKey}
            style={{
              background: '#000', color: '#0f0', padding: '14px', margin: '1rem 0',
              border: '2px solid #0f0', borderRadius: '6px', fontFamily: 'monospace',
              fontSize: '0.7rem', fontWeight: 'bold', cursor: 'pointer', userSelect: 'all',
              textAlign: 'center', boxShadow: '0 0 20px rgba(0,255,0,0.3)', transition: 'all 0.3s'
            }}
            onMouseOver={e => e.currentTarget.style.boxShadow = '0 0 30px rgba(0,255,0,0.6)'}
            onMouseOut={e => e.currentTarget.style.boxShadow = '0 0 20px rgba(0,255,0,0.3)'}
          >
            {key}
          </div>
          <p style={{opacity: 0.8, fontSize: '0.65rem', marginTop: '0.5rem'}}>
            Это ваш триал-ключ на 3 дня · После — продлите в ЛК
          </p>

          <p><strong>3.</strong> Откройте приложение <strong>V2RayNG</strong>, <strong>Nekobox</strong>, <strong>v2rayN</strong> или другое</p>
          <p>
            → Нажмите «+» или «Импорт»<br />
            → «Из буфера обмена»<br />
            → Готово! Подключайтесь
          </p>

          <div style={{marginTop: '1.5rem', textAlign: 'center'}}>
            <button
              onClick={() => window.location.hash = '#lk'}
              style={{
                background: 'transparent', color: '#0f0', border: '2px solid #0f0',
                padding: '12px 24px', borderRadius: '12px', fontWeight: 'bold',
                fontSize: '0.9rem', cursor: 'pointer', boxShadow: '0 0 20px rgba(0,255,0,0.4)'
              }}
            >
              Личный кабинет
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}