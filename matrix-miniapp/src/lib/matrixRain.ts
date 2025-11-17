export function initMatrixRain() {
  const canvas = document.getElementById('matrix-canvas') as HTMLCanvasElement;
  const ctx = canvas.getContext('2d')!;
  
  let fontSize = 16;
  let drops: number[] = [];
  
  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    // Пересчитываем колонки при ресайзе
    const columns = Math.floor(canvas.width / fontSize);
    drops = Array(columns).fill(1);
  };
  
  resize();
  window.addEventListener('resize', resize);
  
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
  
  const draw = () => {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0f0';
    ctx.font = `${fontSize}px monospace`;
    
    for (let i = 0; i < drops.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillText(char, i * fontSize, drops[i] * fontSize);
      
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  };
  
  setInterval(draw, 33);
}