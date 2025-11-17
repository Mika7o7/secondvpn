import { getPrice } from '../../utils';

interface ExtendKeyModalProps {
  keyData: { id: string; name: string; expires: string };
  months: string;
  setMonths: (v: string) => void;
  onPay: (type: 'bonuses' | 'sbp') => void;
  onClose: () => void;
}

export default function ExtendKeyModal({ keyData, months, setMonths, onPay, onClose }: ExtendKeyModalProps) {
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.96)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={onClose}>
      <div style={{ background: 'rgba(0,35,0,0.98)', border: '1px solid #0f0', borderRadius: '16px', padding: '0.8rem', width: '88%', maxWidth: '380px', boxShadow: '0 0 50px rgba(0,255,0,0.7)' }} onClick={e => e.stopPropagation()}>
        <h3 style={{ color: '#0f0', fontSize: '0.95rem', marginBottom: '1rem', textAlign: 'center' }}>Продлить доступ</h3>
        
        <p style={{ fontSize: '0.6rem', opacity: 0.9, textAlign: 'center', margin: '0.8rem 0' }}>
          Ключ: <strong style={{ color: '#0f0' }}>{keyData.name}</strong>
        </p>
        
        <input
          type="number"
          placeholder="Месяцев"
          value={months}
          onChange={e => setMonths(e.target.value)}
          style={{ width: '80%', padding: '10px', marginBottom: '0.8rem', background: '#000', border: '1px solid #0f0', color: '#0f0', borderRadius: '8px', fontSize: '0.6rem' }}
        />
        
        <p style={{ fontSize: '0.6rem', opacity: 0.9, textAlign: 'center', margin: '0.8rem 0' }}>
          Стоимость: <strong style={{ color: '#0f0' }}>{months ? getPrice(parseInt(months) || 0) : 0} ₽</strong>
          {months === '3' && ' · Акция!'} {months === '6' && ' · Акция!'} {months === '12' && ' · Лучшая цена!'}
        </p>
        
        <div style={{ display: 'flex', gap: '8px', marginTop: '1rem' }}>
          <button onClick={() => onPay('bonuses')} style={{ flex: 1, background: 'transparent', color: '#0f0', border: '1px solid #0f0', padding: '12px', borderRadius: '10px', fontSize: '0.6rem', fontWeight: 'bold' }}>
            Бонусами
          </button>
          <button onClick={() => onPay('sbp')} style={{ flex: 1, background: '#0f0', color: '#000', padding: '12px', borderRadius: '10px', fontSize: '0.6rem', fontWeight: 'bold' }}>
            По СБП
          </button>
        </div>
        
        <button onClick={onClose} style={{ width: '100%', marginTop: '0.8rem', background: 'transparent', color: '#0f0', border: '1px solid #0f0', padding: '10px', borderRadius: '8px', fontSize: '0.6rem', fontWeight: 'bold' }}>
          Отмена
        </button>
      </div>
    </div>
  );
}