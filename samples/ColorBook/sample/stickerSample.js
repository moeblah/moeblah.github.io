
  const canvas = document.getElementById('sticker');
  const ctx = canvas.getContext('2d');

  let sticker = new Image();
  sticker.src = 'sample/sticker.png'; // 스티커 이미지 경로

  let stickerX = 100, stickerY = 100; // 스티커 초기 위치
  let stickerWidth = 100, stickerHeight = 100; // 스티커 초기 크기
  let stickerRotation = 0; // 스티커 초기 회전 각도

  let isDragging = false;
  let isResizing = false;
  let isRotating = false;
  let startX, startY;
  let aspectRatio;

  sticker.onload = () => {
    aspectRatio = sticker.width / sticker.height;
    draw();
  };

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(stickerX + stickerWidth / 2, stickerY + stickerHeight / 2);
    ctx.rotate(stickerRotation);
    ctx.drawImage(sticker, -stickerWidth / 2, -stickerHeight / 2, stickerWidth, stickerHeight);
    ctx.restore();
    drawHandles();
  }

  function drawHandles() {
    ctx.save();
    ctx.translate(stickerX + stickerWidth / 2, stickerY + stickerHeight / 2);
    ctx.rotate(stickerRotation);

    // Resize handle
    ctx.fillStyle = 'blue';
    ctx.fillRect(stickerWidth / 2 - 5, stickerHeight / 2 - 5, 10, 10);

    // Rotate handle
    ctx.fillStyle = 'red';
    ctx.beginPath();
    ctx.arc(0, -stickerHeight / 2 - 20, 10, 0, 2 * Math.PI);
    ctx.fill();

    ctx.restore();
  }

  canvas.addEventListener('mousedown', (e) => {
    startX = e.offsetX;
    startY = e.offsetY;
    if (isInsideSticker(startX, startY)) {
      isDragging = true;
    } else if (isOnResizeHandle(startX, startY)) {
      isResizing = true;
    } else if (isOnRotateHandle(startX, startY)) {
      isRotating = true;
    }
  });

  canvas.addEventListener('mousemove', (e) => {
    if (isDragging) {
      let dx = e.offsetX - startX;
      let dy = e.offsetY - startY;
      stickerX += dx;
      stickerY += dy;
      startX = e.offsetX;
      startY = e.offsetY;
      draw();
    } else if (isResizing) {
      let dx = e.offsetX - startX;
      let dy = e.offsetY - startY;
      stickerWidth += dx;
      stickerHeight = stickerWidth / aspectRatio;
      startX = e.offsetX;
      startY = e.offsetY;
      draw();
    } else if (isRotating) {
      let centerX = stickerX + stickerWidth / 2;
      let centerY = stickerY + stickerHeight / 2;
      let dx = e.offsetX - centerX;
      let dy = e.offsetY - centerY;
      stickerRotation = Math.atan2(dy, dx) - Math.PI / 2;
      draw();
    }
  });

  canvas.addEventListener('mouseup', () => {
    isDragging = false;
    isResizing = false;
    isRotating = false;
  });

  function isInsideSticker(x, y) {
    ctx.save();
    ctx.translate(stickerX + stickerWidth / 2, stickerY + stickerHeight / 2);
    ctx.rotate(stickerRotation);
    ctx.beginPath();
    ctx.rect(-stickerWidth / 2, -stickerHeight / 2, stickerWidth, stickerHeight);
    ctx.restore();
    return ctx.isPointInPath(x, y);
  }

  function isOnResizeHandle(x, y) {
    ctx.save();
    ctx.translate(stickerX + stickerWidth / 2, stickerY + stickerHeight / 2);
    ctx.rotate(stickerRotation);
    ctx.beginPath();
    ctx.rect(stickerWidth / 2 - 10, stickerHeight / 2 - 10, 20, 20);
    ctx.restore();
    return ctx.isPointInPath(x, y);
  }

  function isOnRotateHandle(x, y) {
    ctx.save();
    ctx.translate(stickerX + stickerWidth / 2, stickerY + stickerHeight / 2);
    ctx.rotate(stickerRotation);
    ctx.beginPath();
    ctx.arc(0, -stickerHeight / 2 - 20, 10, 0, 2 * Math.PI);
    ctx.restore();
    return ctx.isPointInPath(x, y);
  }
