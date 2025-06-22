let generatedCaptcha = '';

function generateCaptcha() {
  const canvas = document.getElementById('captchaCanvas');
  const ctx = canvas.getContext('2d');

  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  generatedCaptcha = '';
  for (let i = 0; i < 6; i++) {
    generatedCaptcha += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Set background
  ctx.fillStyle = '#f0f0f0';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw captcha text
  ctx.font = '24px Arial';
  ctx.fillStyle = '#000';

  for (let i = 0; i < generatedCaptcha.length; i++) {
    const x = 10 + i * 18;
    const y = 25 + Math.random() * 8;
    const angle = Math.random() * 0.5 - 0.25;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.fillText(generatedCaptcha[i], 0, 0);
    ctx.restore();
  }

  // Optional: Add noise lines
  for (let i = 0; i < 5; i++) {
    ctx.strokeStyle = 'rgba(0,0,0,0.2)';
    ctx.beginPath();
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.stroke();
  }
}

function validateCaptcha() {
  const inputCaptcha = document.getElementById('captcha').value.trim();
  if (inputCaptcha.toUpperCase() !== generatedCaptcha.toUpperCase()) {
    alert('Invalid Captcha. Please try again.');
    generateCaptcha();
    return false;
  }
  return true;
}

// Generate on page load
window.onload = generateCaptcha;
