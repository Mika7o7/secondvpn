// src/components/modals/PaymentModal.tsx
import { getPrice } from '../../utils';
import { useState } from 'react';
import SuccessModal from './SuccessModal'; // ← ДОБАВЬ ЭТОТ ИМПОРТ

interface PaymentModalProps {
  type: 'sbp' | 'bonuses';
  months: string;
  sbpCode: string | null;
  loading: boolean;
  onInitSbp: () => void;
  onConfirmSbp: () => void;
  onBonusPayment: () => void;
  onClose: () => void;
  onCopySuccess?: () => void;
}

export default function PaymentModal({
  type,
  months,
  sbpCode,
  loading,
  onInitSbp,
  onConfirmSbp,
  onBonusPayment,
  onClose,
  onCopySuccess
}: PaymentModalProps) {
  const [showCopySuccess, setShowCopySuccess] = useState(false);

  // === БОНУСЫ ===
  if (type === 'bonuses') {
    return (
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.97)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={onClose}>
        <div style={{ background: 'rgba(0,30,0,0.98)', border: '2px solid #0f0', borderRadius: '16px', padding: '1.2rem', width: '90%', maxWidth: '400px', boxShadow: '0 0 70px rgba(0,255,0,0.9)', textAlign: 'center' }} onClick={e => e.stopPropagation()}>
          <h3 style={{ color: '#0f0', fontSize: '0.95rem', marginBottom: '1rem' }}>Оплата бонусами</h3>
          <p style={{ fontSize: '0.6rem', lineHeight: '1.6', opacity: 0.9 }}>
            Списано <strong style={{ color: '#0f0' }}>
              {parseInt(months) * 30} бонусов
            </strong><br />
            (1 бонус = 1 день)
          </p>
          <button
            onClick={onBonusPayment}
            disabled={loading}
            style={{
              marginTop: '1.2rem', background: '#0f0', color: '#000',
              padding: '14px', borderRadius: '12px', width: '100%',
              fontWeight: 'bold', fontSize: '0.7rem'
            }}
          >
            {loading ? 'Обрабатываем...' : 'Готово'}
          </button>
        </div>
      </div>
    );
  }

  // === СБП ===
  return (
    <>
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.97)', zIndex: 1001, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={onClose}>
        <div style={{ background: 'rgba(0,30,0,0.98)', border: '2px solid #0f0', borderRadius: '16px', padding: '0.8rem', width: '90%', maxWidth: '400px', boxShadow: '0 0 70px rgba(0,255,0,0.9)', textAlign: 'center' }} onClick={e => e.stopPropagation()}>
          <h3 style={{ color: '#0f0', fontSize: '0.95rem', marginBottom: '1rem' }}>Оплата по СБП</h3>

          {/* ВНИМАНИЕ + КОД */}
          <div style={{
            background: '#000', padding: '1.2rem', borderRadius: '12px',
            margin: '1rem 0', border: '1px dashed #0f0', position: 'relative'
          }}>
            {/* Жёлтый треугольник */}
            <div style={{
              position: 'absolute', top: '-10px', left: '16px',
              width: 0, height: 0,
              borderLeft: '10px solid transparent',
              borderRight: '10px solid transparent',
              borderBottom: '10px solid #ff0'
            }}></div>

            <p style={{ fontSize: '0.65rem', margin: '0 0 0.8rem', color: '#ff0', fontWeight: 'bold', textAlign: 'center' }}>
              ВНИМАНИЕ!
            </p>
            <p style={{ fontSize: '0.6rem', margin: '0 0 1rem', opacity: 0.9, lineHeight: '1.5', textAlign: 'center' }}>
              Чтобы оплата прошла <strong>автоматически</strong>,<br />
              обязательно укажи в комментарии к платежу этот код:
            </p>

            {/* КЛИКАБЕЛЬНЫЙ КОД */}
            {sbpCode ? (
              <div
                onClick={() => {
                  navigator.clipboard.writeText(sbpCode);
                  setShowCopySuccess(true);
                  onCopySuccess?.(); // ← если хочешь и в LkPage
                }}
                style={{
                  background: '#111', color: '#0f0', padding: '14px 18px',
                  border: '2px solid #0f0', borderRadius: '12px',
                  fontFamily: 'monospace', fontSize: '1.3rem', fontWeight: 'bold',
                  textAlign: 'center', cursor: 'pointer', userSelect: 'none',
                  margin: '0.8rem 0', boxShadow: '0 0 25px rgba(0,255,0,0.5)',
                  transition: 'all 0.2s'
                }}
                onMouseOver={e => e.currentTarget.style.boxShadow = '0 0 40px rgba(0,255,0,0.8)'}
                onMouseOut={e => e.currentTarget.style.boxShadow = '0 0 25px rgba(0,255,0,0.5)'}
              >
                {sbpCode}
              </div>
            ) : (
              <p style={{ color: '#0f0', fontSize: '0.8rem', opacity: 0.7, textAlign: 'center' }}>
                Нажми «Получить код» ниже
              </p>
            )}
          </div>

          {/* КНОПКИ */}
          {!sbpCode && (
            <button onClick={onInitSbp} disabled={loading} style={{
              width: '100%', background: '#0f0', color: '#000', padding: '14px', borderRadius: '12px',
              fontWeight: 'bold', fontSize: '0.7rem', margin: '0.5rem 0'
            }}>
              {loading ? 'Генерируем...' : 'Получить код'}
            </button>
          )}
          {sbpCode && (
            <a href="https://pay.cloudtips.ru/p/dd5af2bf" target="_blank" rel="noopener noreferrer" style={{
              display: 'block', background: '#0f0', color: '#000', padding: '14px', borderRadius: '12px',
              textDecoration: 'none', fontWeight: 'bold', fontSize: '0.7rem', margin: '1rem 0'
            }}>
              Перейти к оплате · {getPrice(parseInt(months) || 0)} ₽
            </a>
          )}
          {sbpCode && (
            <button onClick={onConfirmSbp} disabled={loading} style={{
              width: '100%', background: 'transparent', color: '#0f0', border: '1px solid #0f0',
              padding: '12px', borderRadius: '8px', fontSize: '0.6rem', fontWeight: 'bold'
            }}>
              {loading ? 'Проверяем...' : 'Я оплатил'}
            </button>
          )}
        </div>
      </div>

      {/* ← ДОБАВЛЕНО: SUCCESS MODAL ДЛЯ КОПИРОВАНИЯ */}
      {showCopySuccess && (
        <SuccessModal
          message="Код скопирован в буфер!"
          onClose={() => setShowCopySuccess(false)}
        />
      )}
    </>
  );
}