interface ErrorModalProps {
  message: string;
  onClose: () => void;
}

export default function ErrorModal({ message, onClose }: ErrorModalProps) {
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.95)', zIndex: 2000,
      display: 'flex', alignItems: 'center', justifyContent: 'center'
    }} onClick={onClose}>
      <div style={{
        background: 'rgba(40,0,0,0.98)', border: '3px solid #f55', borderRadius: '20px',
        padding: '1.5rem', width: '88%', maxWidth: '380px', textAlign: 'center',
        boxShadow: '0 0 80px rgba(255,85,85,0.8)', animation: 'shake 0.5s'
      }} onClick={e => e.stopPropagation()}>
        <div style={{ width: '60px', height: '60px', margin: '0 auto 1rem', position: 'relative' }}>
          <div style={{
            position: 'absolute', top: '18px', left: '18px', width: '24px', height: '24px',
            border: '4px solid #f55', borderRadius: '50%'
          }}></div>
          <div style={{
            position: 'absolute', top: '12px', left: '28px', width: '4px', height: '20px',
            background: '#f55', transform: 'rotate(45deg)'
          }}></div>
          <div style={{
            position: 'absolute', top: '12px', left: '28px', width: '4px', height: '20px',
            background: '#f55', transform: 'rotate(-45deg)'
          }}></div>
        </div>
        <h3 style={{ color: '#f55', fontSize: '1.1rem', margin: '0 0 0.8rem' }}>ОШИБКА</h3>
        <p style={{ color: '#f88', fontSize: '0.7rem', lineHeight: '1.5', opacity: 0.9 }}>
          {message}
        </p>
        <button onClick={onClose} style={{
          marginTop: '1.2rem', background: '#f55', color: '#000',
          padding: '14px', borderRadius: '12px', width: '100%', fontWeight: 'bold', fontSize: '0.7rem'
        }}>Понял</button>
      </div>
    </div>
  );
}