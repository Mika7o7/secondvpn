const API_BASE = "http://localhost:8000"; // ← меняй на свой домен в проде

// Универсальная функция, которая кидает ошибку при любом не-200 ответе
const request = async (url: string, options: RequestInit) => {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({})); // если не json — пусто

  if (!res.ok) {
    // FastAPI возвращает { detail: "Недостаточно бонусных дней" } или массив
    const errorMessage = 
      data.detail || 
      (Array.isArray(data.detail) ? data.detail[0]?.msg : null) || 
      data.message || 
      "Ошибка сервера";

    throw new Error(errorMessage);
  }

  return data;
};

export const api = {
  API_BASE,

  // Получить все данные для ЛК
  getMyData: async (userId: number) => {
    return request(`${API_BASE}/api/my-data?user_id=${userId}`, { method: 'GET' });
  },

  createUser: async (tgId: number, username: string, refCode: string | null = null) => {
    return request(`${API_BASE}/api/create_user`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tg_id: tgId,
        username: username || `user_${tgId}`,
        ref_code: refCode,
      }),
    });
  },

  // ← ВАЖНО: теперь кидает ошибку при 400!
  createKey: async (userId: number, deviceName: string, months: number, paymentMethod?: 'bonuses') => {
    return request(`${API_BASE}/api/create-key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        device_name: deviceName,
        months,
        payment_method: paymentMethod || undefined
      })
    });
  },

  // ← и этот тоже теперь кидает ошибку при проблемах
  extendKey: async (
    userId: number,
    keyId: number,
    months: number,
    payment_method: 'sbp' | 'bonuses',
    amount_rub?: number
  ) => {
    const body: any = {
      user_id: userId,
      key_id: keyId,
      months,
      payment_method
    };

    // Только если СБП — передаём сумму
    if (payment_method === 'sbp' && amount_rub !== undefined) {
      body.amount_rub = amount_rub;
    }

    return request(`${API_BASE}/api/extend-key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
  },

  deleteKey: async (userId: number, keyId: number) => {
    return request(`${API_BASE}/api/delete-key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, key_id: keyId })
    });
  },

 initSbpPayment: async (
  userId: number,
  months: number,
  deviceName: string | undefined,
  keyId: number | undefined,
  username: string | undefined  // ← ОБЯЗАТЕЛЬНО ПЕРЕДАЁМ ИЗ ФРОНТА!
) => {
  return request(`${API_BASE}/api/init-sbp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      months,
      device_name: deviceName,
      key_id: keyId,
      username,  // ← теперь передаётся!
    }),
  });
},

confirmSbpPayment: async (code: string) => {
  return request(`${API_BASE}/api/confirm-sbp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });
},
};