import { useState, useEffect } from 'react';  // ← добавил useEffect
import { getPrice, normalizeDeviceName } from '../../utils';

interface AddKeyModalProps {
  months: string;
  // newName и setNewName больше НЕ НУЖНЫ здесь! Убери их из пропсов
  setMonths: (v: string) => void;
  onPay: (type: 'bonuses' | 'sbp', deviceNameForServer: string, displayNameForUI: string) => void;
  onClose: () => void;
}

export default function AddKeyModal({
  months,
  setMonths,
  onPay,
  onClose
}: AddKeyModalProps) {

  // Эти состояния теперь локальные внутри модалки (это правильно!)
  const [displayName, setDisplayName] = useState('');
  const [deviceName, setDeviceName] = useState('');

  // Обновляем транслит при каждом изменении
  useEffect(() => {
    setDeviceName(normalizeDeviceName(displayName));
  }, [displayName]);

  // Блокировка кнопок, если не валидно
  const isValid = displayName.trim().length >= 2 && deviceName.length >= 2 && months && parseInt(months) >= 1;

  const handlePay = (type: 'bonuses' | 'sbp') => {
    if (!isValid) return;
    onPay(type, deviceName, displayName); // ← передаём оба имени наверх
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.96)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={onClose}>
      <div style={{ background: 'rgba(0,35,0,0.98)', border: '1px solid #0f0', borderRadius: '16px', padding: '1.2rem', width: '88%', maxWidth: '360px', boxShadow: '0 0 50px rgba(0,255,0,0.7)' }} onClick={e => e.stopPropagation()}>

        <h3 style={{ color: '#0f0', fontSize: '1.1rem', marginBottom: '1.2rem', textAlign: 'center' }}>
          Новый ключ
        </h3>

        <input
          placeholder="Название устройства (любое)"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          style={{ width: '80%', padding: '12px', marginBottom: '0.8rem', background: '#000', border: '1px solid #0f0', color: '#0f0', borderRadius: '8px', fontSize: '0.9rem' }}
        />

        {/* Опционально: покажи, как будет на сервере */}
        {deviceName && deviceName !== displayName && (
          <div style={{ fontSize: '0.65rem', color: '#0a0', margin: '-0.5rem 0 0.8rem', opacity: 0.8 }}>
            На сервере: <strong>{deviceName}</strong>
          </div>
        )}

        <input
          type="number"
          min="1"
          placeholder="На сколько месяцев?"
          value={months}
          onChange={e => setMonths(e.target.value)}
          style={{ width: '80%', padding: '12px', marginBottom: '1rem', background: '#000', border: '1px solid #0f0', color: '#0f0', borderRadius: '8px', fontSize: '0.9rem' }}
        />

        <p style={{ fontSize: '0.85rem', textAlign: 'center', margin: '0.5rem 0 1rem' }}>
          Стоимость: <strong style={{ color: '#0f0' }}>{months ? getPrice(parseInt(months) || 0) : 0} ₽</strong>
          {months === '3' && ' · Акция!'}
          {months === '6' && ' · Акция!'}
          {months === '12' && ' · Лучшая цена!'}
        </p>

        <div style={{ display: 'flex', gap: '12px', marginTop: '1rem' }}>
          <button
            onClick={() => handlePay('bonuses')}
            disabled={!isValid}
            style={{
              flex: 1,
              background: isValid ? 'transparent' : '#111',
              color: '#0f0',
              border: '1px solid #0f0',
              padding: '14px',
              borderRadius: '10px',
              fontWeight: 'bold',
              opacity: isValid ? 1 : 0.5,
              cursor: isValid ? 'pointer' : 'not-allowed'
            }}>
            Бонусами
          </button>

          <button
            onClick={() => handlePay('sbp')}
            disabled={!isValid}
            style={{
              flex: 1,
              background: isValid ? '#0f0' : '#050',
              color: isValid ? '#000' : '#060',
              padding: '14px',
              borderRadius: '10px',
              fontWeight: 'bold',
              cursor: isValid ? 'pointer' : 'not-allowed'
            }}>
            По СБП
          </button>
        </div>

        <button onClick={onClose} style={{
              flex: 1,
              background: isValid ? 'transparent' : '#111',
              color: '#0f0',
              border: '1px solid #0f0',
              padding: '14px',
              borderRadius: '10px',
              fontWeight: 'bold',
              opacity: isValid ? 1 : 0.5,
              cursor: isValid ? 'pointer' : 'not-allowed',
              width: '100%',
              marginTop: '1rem'
            }}>
          Отмена
        </button>
      </div>
    </div>
  );
}