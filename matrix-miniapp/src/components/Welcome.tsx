// src/components/Welcome.tsx
import { useState } from "react";
import { api } from "../api";

type Props = {
  onClose: () => void;
};

export default function Welcome({ onClose }: Props) {
  const [loading, setLoading] = useState(false);

  const handleContinue = async () => {
    if (loading) return;
    setLoading(true);

    try {
      // ЖЁСТКО ЗАШИТЫЙ ID — только для теста!
      const result = await api.createUser(1628997906, "Mikaggwp", null);
      
      console.log("Триал-ключ успешно создан:", result);
      onClose(); // закрываем Welcome → увидим ключ в ЛК
    } catch (err: any) {
      alert("Ошибка: " + (err.message || "Неизвестная ошибка"));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const downloadApp = (platform: string) => {
    alert(`Загрузка для ${platform}...`);
  };

  return (
    <div id="welcome" style={{
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: '90%',
      maxWidth: '400px',
      textAlign: 'center',
      zIndex: 100,
      animation: 'fadeIn 1s ease-in',
    }}>
      <h1 style={{
        fontSize: 'clamp(2.8rem, 12vw, 5rem)',
        letterSpacing: '0.8rem',
        margin: '0 0 0.5rem 0',
        lineHeight: '1.1',
        fontWeight: 'bold',
      }}>
        MATRIX<br />VPN
      </h1>

      <p className="welcome-text" style={{
        margin: '1.5rem auto 2rem',
        fontSize: '0.78rem',
        lineHeight: '1.5',
        opacity: 0.9,
      }}>
        Добро пожаловать в защищённую сеть.<br />
        Скачайте V2TurnRey и подключитесь за 10 секунд.
      </p>

      <div className="platform-grid" style={{ gap: '10px', marginBottom: '1.8rem' }}>
        <div className="platform-btn" onClick={() => downloadApp('windows')} style={{ padding: '10px 6px', fontSize: '0.8rem', minHeight: '52px' }}>
          <strong style={{ fontSize: '0.9rem' }}>Windows</strong>
          <small style={{ fontSize: '0.65rem' }}>v2RayTun_Setup.exe</small>
        </div>
        <div className="platform-btn" onClick={() => downloadApp('macos')} style={{ padding: '10px 6px', fontSize: '0.8rem', minHeight: '52px' }}>
          <strong style={{ fontSize: '0.9rem' }}>macOS / iOS</strong>
          <small style={{ fontSize: '0.65rem' }}>App Store</small>
        </div>
        <div className="platform-btn" onClick={() => downloadApp('android')} style={{ padding: '10px 6px', fontSize: '0.8rem', minHeight: '52px' }}>
          <strong style={{ fontSize: '0.9rem' }}>Android</strong>
          <small style={{ fontSize: '0.65rem' }}>Google Play</small>
        </div>
        <div className="platform-btn" onClick={() => downloadApp('linux')} style={{ padding: '10px 6px', fontSize: '0.8rem', minHeight: '52px' }}>
          <strong style={{ fontSize: '0.9rem' }}>Linux</strong>
          <small style={{ fontSize: '0.65rem' }}>Hiddify AppImage</small>
        </div>
      </div>

      <div
        className="action-btn"
        onClick={handleContinue}
        style={{
          marginTop: '0.5rem',
          padding: '11px 22px',
          fontSize: '0.95rem',
          fontWeight: 'bold',
          minWidth: '180px',
          display: 'inline-block',
          opacity: loading ? 0.6 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? "Создаём ключ..." : "Понял, показать ключ"}
      </div>
    </div>
  );
}