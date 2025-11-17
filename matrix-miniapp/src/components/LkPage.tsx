// src/components/LkPage.tsx
import { useEffect, useState } from 'react';
import { api } from '../api';
import KeyCard from './ui/KeyCard';
import AddKeyModal from './modals/AddKeyModal';
import ExtendKeyModal from './modals/ExtendKeyModal';
import PaymentModal from './modals/PaymentModal';
import SuccessModal from './modals/SuccessModal';
import ErrorModal from './modals/ErrorModal';
import { formatDate, getPrice, generateSequentialDeviceName } from '../utils';

interface Key {
  id: string;
  name: string;
  key: string;
  expires: string;
}

interface UserData {
  keys: Key[];
  bonus_days: number;
  referrals_count: number;
  ref_link: string;
}

export default function LkPage() {
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 1628997906;

  const [keys, setKeys] = useState<Key[]>([]);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  // Модальные состояния
  const [showAddModal, setShowAddModal] = useState(false);
  const [showExtendModal, setShowExtendModal] = useState<Key | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState<'bonuses' | 'sbp' | null>(null);
  const [showSuccess, setShowSuccess] = useState<string | null>(null);
  const [showError, setShowError] = useState<string | null>(null);
  const [sbpCode, setSbpCode] = useState<string | null>(null);
  const [months, setMonths] = useState('');
  const [tempDisplayName, setTempDisplayName] = useState('');
  const [tempDeviceName, setTempDeviceName] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<Key | null>(null);
  const [showRefCopySuccess, setShowRefCopySuccess] = useState(false);

  // === ОБНОВЛЕНИЕ ДАННЫХ С СЕРВЕРА ===
  const refreshData = async () => {
    try {
      const data = await api.getMyData(userId);
      setUserData(data);
      setKeys(data.keys || []);
    } catch (err: any) {
      setShowError('Ошибка связи с сервером');
    }
  };

  // Загрузка при старте
  useEffect(() => {
    refreshData().finally(() => setLoading(false));
  }, [userId]);

  // === СБП: ИНИЦИАЛИЗАЦИЯ ===
const initSbp = async () => {
  console.log("initSbp: START", { months, tempDeviceName, showExtendModal });

  if (!months || !tempDeviceName) {
    setShowError('Ошибка: выбери срок и устройство');
    return;
  }
  try {
    let targetUsername = "mikaggwp";
    if (showExtendModal && showExtendModal.id) {
      const key = keys.find(k => k.id === showExtendModal.id);
      if (key?.username) {
        targetUsername = key.username;
      }
    } else if (keys.length > 0 && keys[0]?.username) {
      targetUsername = keys[0].username;
    }

    const res = await api.initSbpPayment(
      userId,
      parseInt(months),
      tempDeviceName,
      showExtendModal ? parseInt(showExtendModal.id) : undefined,
      targetUsername
    );
    setSbpCode(res.code);
    // setShowPaymentModal('sbp');
  } catch (err: any) {
    console.error("SBP init error:", err);
    setShowError(err.message || 'Не удалось получить код оплаты');
  }
};

// === СБП: ПОДТВЕРЖДЕНИЕ ===
const confirmSbp = async () => {
  if (!sbpCode) return;

  setLoading(true);
  try {
    const result = await api.confirmSbpPayment(sbpCode);

    if (result.success) {
      setShowSuccess(
        showAddModal
          ? `Ключ "${tempDisplayName}" успешно создан!`
          : result.message || `Продлено на ${months} мес.!`
      );
    }
  } catch (err: any) {
    const msg = err.message || 'Платёж не прошёл';
    if (msg.includes('не найден') || msg.includes('комментари')) {
      setShowError('Платёж не найден. Убедись, что в комментарии указан код: ' + sbpCode);
    } else {
      setShowError(msg);
    }
  } finally {
    await refreshData();
    setLoading(false);
    setShowPaymentModal(null);
    setShowAddModal(false);
    setShowExtendModal(null);
    setSbpCode(null);
    setTempDisplayName('');
    setTempDeviceName('');
    setMonths('');
  }
};

  // === БОНУСЫ: ОПЛАТА (ГЛАВНОЕ ИСПРАВЛЕНИЕ) ===
  const handleBonusPayment = async (deviceNameForServer: string, displayNameForUI: string) => {
    if (!months || parseInt(months) < 1) {
      setShowError('Укажи количество месяцев');
      return;
    }

    const m = parseInt(months);
    setLoading(true);

    try {
      if (showAddModal) {
        await api.createKey(userId, deviceNameForServer, m, 'bonuses');
        setShowSuccess(`Ключ "${displayNameForUI}" создан за бонусы!`);
      } else if (showExtendModal) {
        await api.extendKey(userId, parseInt(showExtendModal.id), m, 'bonuses');
        setShowSuccess(`Ключ "${showExtendModal.name}" продлён за бонусы!`);
      }
    } catch (err: any) {
      setShowError(err.message || 'Недостаточно бонусных дней');
      return; // ← ключ НЕ добавляется при ошибке
    } finally {
      await refreshData(); // ← ВСЁГДА обновляем реальные данные
      setLoading(false);
      setShowPaymentModal(null);
      setShowAddModal(false);
      setShowExtendModal(null);
      setTempDisplayName('');
      setTempDeviceName('');
      setMonths('');
    }
  };

  // === LOADING ===
  if (loading) {
    return <div style={{ color: '#0f0', textAlign: 'center', padding: '3rem' }}>Загрузка...</div>;
  }

  // === ОСНОВНОЙ UI ===
  return (
    <div style={{ textAlign: 'center', padding: '2rem 1rem', minHeight: '100vh' }}>
      <h1 style={{ fontSize: 'clamp(2.8rem, 12vw, 5rem)', letterSpacing: '0.8rem', fontWeight: 'bold' }}>
        MATRIX<br />VPN
      </h1>

      {/* ИНФО ПОЛЬЗОВАТЕЛЯ */}
      <div style={{ margin: '2rem auto 1rem', maxWidth: '600px', textAlign: 'left', fontSize: '0.7rem', opacity: 0.8 }}>
        <p>Бонусных дней: <strong style={{ color: '#0f0' }}>{userData?.bonus_days || 0}</strong></p>
        <p>Приглашено: <strong style={{ color: '#0f0' }}>{userData?.referrals_count || 0}</strong></p>
        <button
          onClick={() => {
            navigator.clipboard.writeText(userData?.ref_link || '');
            setShowRefCopySuccess(true);
          }}
          style={{ background: 'transparent', color: '#0f0', border: '1px solid #0f0', padding: '8px 16px', borderRadius: '8px', fontSize: '0.7rem' }}
        >
          Скопировать реф. ссылку
        </button>
      </div>

      {/* КЛЮЧИ */}
      <div style={{ margin: '1rem auto 2rem', maxWidth: '600px' }}>
        <h2 style={{ color: '#0f0', fontSize: '1.2rem', marginBottom: '1rem' }}>Твои ключи</h2>
        <p style={{ opacity: 0.8, marginBottom: '1.2rem', fontSize: '0.7rem' }}>
          Активно: <strong style={{ color: '#0f0' }}>{keys.length}</strong>
        </p>

        <div style={{
          height: '340px',
          overflowY: 'auto',
          background: 'rgba(0,30,0,0.25)',
          border: '1px solid rgba(0,255,0,0.4)',
          borderRadius: '16px',
          padding: '1rem',
          marginBottom: '1rem'
        }}>
          {keys.length === 0 ? (
            <p style={{ color: '#0f0', opacity: 0.6, fontSize: '0.8rem' }}>Нет ключей. Нажми +</p>
          ) : (
            keys.map(k => (
              <KeyCard
                key={k.id}
                keyData={k}
                onEdit={() => {}}
                onExtend={() => setShowExtendModal(k)}
                onDelete={() => setShowDeleteConfirm(k)}  // ← вот тут открываем модалку
                onCopy={() => {
                  navigator.clipboard.writeText(k.key);
                  alert('Скопировано!');
                }}
              />
            ))
          )}
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          style={{
            background: 'rgba(0,255,0,0.3)',
            color: '#0f0',
            border: '2px solid #0f0',
            padding: '14px',
            borderRadius: '14px',
            fontWeight: 'bold',
            fontSize: '0.6rem',
            width: '100%',
            boxShadow: '0 0 30px rgba(0,255,0,0.5)'
          }}
        >
          + Добавить новый ключ
        </button>
      </div>

      {/* МОДАЛКИ */}
      {showAddModal && (
        <AddKeyModal
          months={months}
          setMonths={setMonths}
          onPay={async (type, userInputDisplayName = '') => {
            if (!months || parseInt(months) < 1) return;

            const telegramUsername =
              window.Telegram?.WebApp?.initDataUnsafe?.user?.username ||
              window.Telegram?.WebApp?.initDataUnsafe?.user?.first_name?.replace(/\s+/g, '') ||
              'user';

            const { serverName, displayName } = generateSequentialDeviceName(
              telegramUsername,
              keys,
              userInputDisplayName
            );

            setTempDeviceName(serverName);
            setTempDisplayName(displayName);

            if (type === 'bonuses') {
              await handleBonusPayment(serverName, displayName);
            } else {
              setShowPaymentModal('sbp');
            }
          }}
          onClose={() => {
            setShowAddModal(false);
            setMonths('');
          }}
        />
      )}

      {showExtendModal && (
        <ExtendKeyModal
          keyData={showExtendModal}
          onClose={() => setShowExtendModal(null)}
          onPay={type => {
            // ← ВОТ ТУТ КЛЮЧЕВОЙ МОМЕНТ
            if (type === 'sbp') {
              setTempDeviceName(showExtendModal.name);     // ← УСТАНАВЛИВАЕМ
              setTempDisplayName(showExtendModal.name);    // ← ДЛЯ UI
            }
            setShowPaymentModal(type);
          }}
          months={months}
          setMonths={setMonths}
        />
      )}

      {showPaymentModal && (
        <PaymentModal
          type={showPaymentModal}
          months={months}
          sbpCode={sbpCode}
          loading={loading}
          onInitSbp={initSbp}
          onConfirmSbp={confirmSbp}
          onBonusPayment={() => handleBonusPayment(tempDeviceName, tempDisplayName)}
          onClose={() => setShowPaymentModal(null)}
        />
      )}

      {/* === КРАСИВОЕ КРАСНОЕ ОКНО ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ === */}
      {showDeleteConfirm && (
        <div 
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.95)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000
          }} 
          onClick={() => setShowDeleteConfirm(null)}
        >
          <div 
            style={{
              background: 'rgba(60,0,0,0.98)', 
              border: '2px solid #f55', 
              borderRadius: '16px',
              padding: '2rem', 
              maxWidth: '90%', 
              textAlign: 'center', 
              boxShadow: '0 0 50px rgba(255,0,0,0.8)'
            }} 
            onClick={e => e.stopPropagation()}
          >
            <h3 style={{ color: '#f55' }}>
              Удалить ключ?
            </h3>
            <p style={{ color: '#fcc', marginBottom: '1rem', fontSize: '0.8rem' }}>
              <strong style={{ color: '#fcc', marginBottom: '1rem', fontSize: '1rem' }}>{showDeleteConfirm.name}</strong><br /><br />
              Это действие <strong>нельзя</strong> отменить!
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button 
                onClick={async () => {
                  try {
                    await api.deleteKey(userId, parseInt(showDeleteConfirm.id));
                  
                    // УБИРАЕМ await — пусть обновляется в фоне
                    refreshData();  // ← БЕЗ await!
                  
                    // Сразу показываем успех — пользователь не ждёт
                    setShowSuccess('Ключ удалён');

                    // Через 800 мс принудительно обновим список (на всякий случай)
                    setTimeout(() => {
                      refreshData();
                    }, 800);
                  
                  } catch (err: any) {
                    setShowError(err.message || 'Ошибка удаления');
                  } finally {
                    setShowDeleteConfirm(null);
                  }
                }}
                style={{
                  background: '#f55', 
                  color: '#000', 
                  padding: '10px 30px', 
                  border: 'none',
                  borderRadius: '10px', 
                  fontWeight: 'bold', 
                  fontSize: '0.7rem',
                  boxShadow: '0 0 20px rgba(255,0,0,0.6)'
                }}
              >
                УДАЛИТЬ
              </button>
              <button 
                onClick={() => setShowDeleteConfirm(null)} 
                style={{
                  background: 'transparent', 
                  color: '#0f0', 
                  border: '2px solid #0f0',
                  padding: '10px 30px', 
                  borderRadius: '10px', 
                  fontWeight: 'bold',
                  fontSize: '0.7rem'
                }}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {showRefCopySuccess && (
        <SuccessModal
          message="Реф. ссылка скопирована!"
          onClose={() => setShowRefCopySuccess(false)}
        />
      )}

      {showSuccess && <SuccessModal message={showSuccess} onClose={() => setShowSuccess(null)} />}
      {showError && <ErrorModal message={showError} onClose={() => setShowError(null)} />}
    </div>
  );
}