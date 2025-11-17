interface SuccessModalProps {
  message: string;
  onClose: () => void;
}

export default function SuccessModal({ message, onClose }: SuccessModalProps) {
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.95)', zIndex: 2000,
      display: 'flex', alignItems: 'center', justifyContent: 'center'
    }} onClick={onClose}>
      <div style={{
        background: 'rgba(0,40,0,0.98)', border: '3px solid #0f0', borderRadius: '20px',
        padding: '1.5rem', width: '88%', maxWidth: '380px', textAlign: 'center',
        boxShadow: '0 0 80px rgba(0,255,0,0.9)', animation: 'pulse 1.5s infinite'
      }} onClick={e => e.stopPropagation()}>
        <div style={{
          width: '60px', height: '60px', margin: '0 auto 1rem',
          border: '4px solid #0f0', borderRadius: '50%', position: 'relative'
        }}>
          <div style={{
            position: 'absolute', top: '12px', left: '18px', width: '12px', height: '24px',
            border: '3px solid #0f0', borderTop: 'none', borderLeft: 'none',
            transform: 'rotate(45deg)'
          }}></div>
        </div>
        <h3 style={{ color: '#0f0', fontSize: '1.1rem', margin: '0 0 0.8rem' }}>УСПЕШНО!</h3>
        <p style={{ color: '#0f0', fontSize: '0.7rem', lineHeight: '1.5', opacity: 0.9, whiteSpace: 'pre-line' }}>
          {message}
        </p>
        <button onClick={onClose} style={{
          marginTop: '1.2rem', background: '#0f0', color: '#000',
          padding: '14px', borderRadius: '12px', width: '100%', fontWeight: 'bold', fontSize: '0.7rem'
        }}>Отлично!</button>
      </div>
    </div>
  );
}