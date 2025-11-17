// src/components/ui/KeyCard.tsx
import { formatDate } from '../../utils';

interface KeyCardProps {
  keyData: { id: string; name: string; key: string; expires: string };
  onEdit: () => void;
  onExtend: () => void;
  onDelete: () => void;  // ← просто функция, ничего не знает про модалку
  onCopy: () => void;
}

export default function KeyCard({ keyData, onEdit, onExtend, onDelete, onCopy }: KeyCardProps) {
  return (
    <div style={{
      background: 'rgba(0, 50, 0, 0.6)',
      border: '1px solid #0f0',
      borderRadius: '14px',
      padding: '1.2rem',
      marginBottom: '1rem',
      boxShadow: '0 0 25px rgba(0,255,0,0.25)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
        <strong style={{ fontSize: '0.6rem', cursor: 'pointer', color: '#0f0' }} onClick={onEdit}>
          {keyData.name}
        </strong>
        <span style={{ fontSize: '0.5rem', opacity: 0.7 }}>до {formatDate(keyData.expires)}</span>
      </div>

      <div
        onClick={onCopy}
        style={{
          background: '#000', color: '#0f0', padding: '10px', border: '2px solid #0f0',
          borderRadius: '10px', fontFamily: 'monospace', fontSize: '0.55rem', fontWeight: 'bold',
          cursor: 'pointer', textAlign: 'center', marginBottom: '1rem', wordBreak: 'break-all',
          boxShadow: '0 0 20px rgba(0,255,0,0.5)', transition: 'all 0.3s'
        }}
        onMouseOver={e => e.currentTarget.style.boxShadow = '0 0 40px rgba(0,255,0,0.8)'}
        onMouseOut={e => e.currentTarget.style.boxShadow = '0 0 20px rgba(0,255,0,0.5)'}
      >
        {keyData.key}
      </div>

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
        <button onClick={onExtend} style={{
          background: 'transparent', color: '#0f0', border: '1px solid #0f0',
          padding: '10px 18px', borderRadius: '8px', fontSize: '0.6rem', fontWeight: 'bold'
        }}>
          Продлить
        </button>
        <button onClick={onDelete} style={{  // ← просто вызываем onDelete
          background: 'transparent',
          color: '#f55',
          border: '1px solid #f55',
          padding: '10px 18px',
          borderRadius: '8px',
          fontSize: '0.6rem',
          fontWeight: 'bold'
        }}>
          Удалить
        </button>
      </div>
    </div>
  );
}