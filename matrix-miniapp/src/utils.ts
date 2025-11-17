export const getPrice = (m: number): number => {
  if (m === 3) return 250;
  if (m === 6) return 450;
  if (m === 12) return 800;
  return m * 100;
};

export const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr.replace(' ', 'T'));
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
};


export const normalizeDeviceName = (name: string): string => {
  const translit: Record<string, string> = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i',
    'й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t',
    'у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y',
    'ь':'','э':'e','ю':'yu','я':'ya'
  };

  return name.trim()
    .toLowerCase()
    .split('')
    .map(c => translit[c] || c)
    .join('')
    .replace(/[^a-z0-9._ -]+/g, '')   // убираем всё запрещённое
    .replace(/\s+/g, '_')
    .slice(0, 50);                    // ограничение длины
};

export const generateSequentialDeviceName = (
  username: string,
  existingKeys: Key[],
  userInputDisplayName?: string
): { serverName: string; displayName: string } => {
  // Если пользователь ввёл что-то сам — оставляем его вариант (но транслитим для сервера)
  if (userInputDisplayName && userInputDisplayName.trim()) {
    const display = userInputDisplayName.trim();
    return {
      displayName: display,
      serverName: normalizeDeviceName(display), // у тебя уже есть эта функция
    };
  }

  // Автогенерация: ищем самый большой номер вида username_5
  const pattern = new RegExp(`^${username}_(\\d+)$`, 'i');
  let maxNum = 0;

  existingKeys.forEach((key) => {
    const match = key.name.match(pattern);
    if (match && parseInt(match[1]) > maxNum) {
      maxNum = parseInt(match[1]);
    }
  });

  const nextNum = maxNum + 1;
  const autoName = `${username}_${nextNum}`;

  return {
    displayName: autoName,  // показываем пользователю
    serverName: autoName,   // отправляем на сервер (уже чистое)
  };
};