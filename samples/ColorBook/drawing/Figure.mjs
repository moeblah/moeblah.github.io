class Figure {
  #source
  #imageData
  #corners

  constructor(source, width, height, x=0, y=0) {
    this.#source = source? new ImageData(source, width, height): new ImageData(width, height)
    this.#imageData = this.source
    this.x = x
    this.y = y
  }

  static createFromImage(path) {
    return new Promise((resolve, reject) => {
      const context = document.createElement('canvas').getContext('2d')
      const image = new Image()
      image.src = path

      image.onload = () => {
        const width = image.width
        const height = image.height

        context.canvas.width = width
        context.canvas.height = height
        context.drawImage(image, 0, 0)
        const figure = new this(context.getImageData(0, 0, width, height).data, image.width, image.height)
        resolve(figure)
      }

      image.onerror = (error) => {
        reject(error)
      }
    })
  }

  get center(){
    return [this.width / 2 + this.x, this.height / 2 + this.y]
  }

  get source() {
    return this.#source
  }

  get sourceWidth() {
    return this.#source.width
  }

  get sourceHeight() {
    return this.#source.height
  }

  get imageData() {
    return this.#imageData
  }

  get width() {
    return this.#imageData.width
  }

  get height() {
    return this.#imageData.height
  }

  get corners(){
    return this.#corners.map(([x, y])=>{return {x: x + this.x, y: y + this.y}})
  }

  getPixel(x, y){
    return [
      this.#getPixelValue(this.#imageData.data, this.width, this.height, x, y, 0),
      this.#getPixelValue(this.#imageData.data, this.width, this.height, x, y, 1),
      this.#getPixelValue(this.#imageData.data, this.width, this.height, x, y, 2),
      this.#getPixelValue(this.#imageData.data, this.width, this.height, x, y, 3),
    ]
  }

  drawImage(figure, x, y, opacity = 1) {
    const srcData = figure.imageData.data
    const srcWidth = figure.width
    const srcHeight = figure.height

    for (let sy = 0; sy < srcHeight; sy++) {
      for (let sx = 0; sx < srcWidth; sx++) {
        const srcIndex = (sy * srcWidth + sx) * 4
        const destX = x + sx
        const destY = y + sy

        if (destX >= 0 && destX < this.width && destY >= 0 && destY < this.height) {
          const destIndex = (destY * this.height + destX) * 4

          const srcAlpha = (srcData[srcIndex + 3] / 255) * opacity
          const destAlpha = this.imageData.data[destIndex + 3] / 255

          // Alpha blending: Src over Dest
          for (let i = 0; i < 3; i++) {
            this.imageData.data[destIndex + i] = Math.round(
              srcData[srcIndex + i] * srcAlpha +
              this.imageData.data[destIndex + i] * destAlpha * (1 - srcAlpha)
            )
          }
          this.imageData.data[destIndex + 3] = Math.round(
            (srcAlpha + destAlpha * (1 - srcAlpha)) * 255
          )
        }
      }
    }
  }

  putImage(figure, x, y) {
    const srcData = figure.imageData.data
    const srcWidth = figure.width
    const srcHeight = figure.height

    for (let sy = 0; sy < srcHeight; sy++) {
      for (let sx = 0; sx < srcWidth; sx++) {
        const srcIndex = (sy * srcWidth + sx) * 4
        const destX = x + sx
        const destY = y + sy

        if (destX >= 0 && destX < this.width && destY >= 0 && destY < this.height) {
          const destIndex = (destY * this.height + destX) * 4

          // Copy the source pixel data directly to source
          for (let i = 0; i < 4; i++) {
            this.imageData.data[destIndex + i] = srcData[srcIndex + i]
          }
        }
      }
    }
  }

  #getTransformSize(width, height, radians){
    const transformWidth = Math.round(Math.abs(width * Math.cos(radians)) + Math.abs(height * Math.sin(radians))) || width
    const transformHeight = Math.round(Math.abs(width * Math.sin(radians)) + Math.abs(height * Math.cos(radians))) || height
    return [transformWidth, transformHeight]
  }

  #getTransformCorners(radians, width, height) {
    const cx = width / 2
    const cy = height / 2

    return [
      [-cx, -cy],
      [cx, -cy],
      [-cx, cy],
      [cx, cy],
    ].map(([x, y]) => {
      const newX = Math.cos(radians) * x - Math.sin(radians) * y + cx
      const newY = Math.sin(radians) * x + Math.cos(radians) * y + cy
      return { x: newX, y: newY }
    })
  }

  #rotate(radians, srcData, srcWidth, srcHeight) {
    const [newWidth, newHeight] = this.#getTransformSize(srcWidth, srcHeight, radians)
    const destData = new Uint8ClampedArray(newWidth * newHeight * 4)

    const cx = srcWidth / 2
    const cy = srcHeight / 2
    const ncx = newWidth / 2
    const ncy = newHeight / 2

    for (let y = 0; y < newHeight; y++) {
      for (let x = 0; x < newWidth; x++) {
        const nx = x - ncx
        const ny = y - ncy

        const originalX = Math.cos(radians) * nx + Math.sin(radians) * ny + cx
        const originalY = -Math.sin(radians) * nx + Math.cos(radians) * ny + cy

        if (
          originalX >= 0 &&
          originalX < srcWidth &&
          originalY >= 0 &&
          originalY < srcHeight
        ) {
          const srcIndex = ((Math.floor(originalY) * srcWidth) + Math.floor(originalX)) * 4
          const destIndex = (y * newWidth + x) * 4

          for (let i = 0; i < 4; i++) {
            destData[destIndex + i] = srcData[srcIndex + i]
          }
        }
      }
    }
    return { data: destData, width: newWidth, height: newHeight }
  }

  #getPixelValue(data, width, height, x, y, c) {
    x = Math.max(0, Math.min(x, width - 1))
    y = Math.max(0, Math.min(y, height - 1))
    return data[(y * width + x) * 4 + c]
  }

  #transformBilinearWidth(srcData, srcWidth, srcHeight, destWidth) {
    const xScale = srcWidth / destWidth
    const destData = new Uint8ClampedArray(destWidth * srcHeight * 4)

    for (let y = 0; y < srcHeight; y++) {
      for (let x = 0; x < destWidth; x++) {
        const gx = x * xScale
        const gxi = Math.floor(gx)
        const gxFraction = gx - gxi

        const indexTL = (y * srcWidth + gxi) * 4
        const indexTR = (y * srcWidth + Math.min(gxi + 1, srcWidth - 1)) * 4

        for (let i = 0; i < 4; i++) {
          const topLeft = srcData[indexTL + i]
          const topRight = srcData[indexTR + i]

          const top = topLeft + (topRight - topLeft) * gxFraction

          const destIndex = (y * destWidth + x) * 4
          destData[destIndex + i] = Math.round(top)
        }
      }
    }
    return { data: destData, width: destWidth, height: srcHeight }
  }

  #transformBilinearHeight(srcData, srcWidth, srcHeight, destHeight) {
    const yScale = srcHeight / destHeight
    const destData = new Uint8ClampedArray(srcWidth * destHeight * 4)

    for (let y = 0; y < destHeight; y++) {
      const gy = y * yScale
      const gyi = Math.floor(gy)
      const gyFraction = gy - gyi

      for (let x = 0; x < srcWidth; x++) {
        const indexTL = (gyi * srcWidth + x) * 4
        const indexBL = (Math.min(gyi + 1, srcHeight - 1) * srcWidth + x) * 4

        for (let i = 0; i < 4; i++) {
          const topLeft = srcData[indexTL + i]
          const bottomLeft = srcData[indexBL + i]

          const value = topLeft + (bottomLeft - topLeft) * gyFraction

          const destIndex = (y * srcWidth + x) * 4
          destData[destIndex + i] = Math.round(value)
        }
      }
    }
    return { data: destData, width: srcWidth, height: destHeight }
  }

  #transformWidth(srcData, srcWidth, srcHeight, destWidth) {
    const xScale = destWidth / srcWidth
    const xStep = 1 / xScale
    const destData = new Uint8ClampedArray(destWidth * srcHeight * 4)

    for (let y = 0; y < srcHeight; y++) {
      for (let x = 0; x < destWidth; x++) {
        const beginX = x * xStep
        const endX = Math.min(beginX + xStep, srcWidth)
        const color = [0, 0, 0, 0]
        let weightSum = 0

        for (let originX = beginX; originX < endX; originX++) {
          let weight = originX - Math.floor(originX)
          weight = originX === beginX ? 1 - weight : weight || 1
          if (originX === beginX) originX = Math.floor(originX)
          const index = (Math.floor(y) * srcWidth + Math.floor(originX)) * 4
          weightSum += weight * srcData[index+3] / 255

          for (let i = 0; i < 4; i++) {
            color[i] += srcData[index + i] * weight
          }
        }

        for (let i = 0; i < 4; i++) {
          const index = (y * destWidth + x) * 4
          destData[index + i] = Math.round(color[i] / weightSum)
        }
      }
    }
    return { data: destData, width: destWidth, height: srcHeight }
  }

  #transformHeight(srcData, srcWidth, srcHeight, destHeight) {
    const yScale = destHeight / srcHeight
    const yStep = 1 / yScale
    const destData = new Uint8ClampedArray(srcWidth * destHeight * 4)

    for (let x = 0; x < srcWidth; x++) {
      for (let y = 0; y < destHeight; y++) {
        const beginY = y * yStep
        const endY = Math.min(beginY + yStep, srcHeight)
        const color = [0, 0, 0, 0]
        let weightSum = 0

        for (let originY = beginY; originY < endY; originY++) {
          let weight = originY - Math.floor(originY)
          weight = originY === beginY ? 1 - weight : weight || 1
          if (originY === beginY) originY = Math.floor(originY)
          const index = (Math.floor(originY) * srcWidth + x) * 4
          weightSum += weight * srcData[index+3] / 255

          for (let i = 0; i < 4; i++) {
            color[i] += srcData[index + i] * weight
          }
        }

        for (let i = 0; i < 4; i++) {
          const index = (y * srcWidth + x) * 4
          destData[index + i] = Math.round(color[i] / weightSum)
        }
      }
    }
    return { data: destData, width: srcWidth, height: destHeight }
  }

  #transform(srcData, srcWidth, srcHeight, destWidth, destHeight){
    const [xScale, yScale] = [destWidth / srcWidth, destHeight / srcHeight]
    let image = {data: srcData, width: srcWidth, height: srcHeight }

    if (xScale <= 0.5){
      image = this.#transformWidth(image.data, image.width, image.height, destWidth)
    } else {
      image = this.#transformBilinearWidth(image.data, image.width, image.height, destWidth)
    }
    if (yScale <= 0.5){
      image = this.#transformHeight(image.data, image.width, image.height, destHeight)
    } else {
      image = this.#transformBilinearHeight(image.data, image.width, image.height, destHeight)
    }
    return image
  }

  transform({width, height, scale, radians}){
    const srcData = this.source.data
    const [srcWidth, srcHeight] = [this.sourceWidth, this.sourceHeight]
    const widthScale = width? width / srcWidth: scale
    const heightScale = height? height / srcHeight: scale
    let source = {data: srcData, width: srcWidth, height: srcHeight}

    if (radians) source = this.#rotate(radians, source.data, source.width, source.height)
    if (widthScale || heightScale) {
      const destWidth = Math.round(source.width * widthScale)
      const destHeight =  Math.round(source.height * heightScale)
      source = this.#transform(source.data, source.width, source.height, destWidth, destHeight)
    }

    this.#imageData = new ImageData(source.data, source.width, source.height)
    this.#corners = this.#getTransformCorners(radians, this.width, this.height)
  }
}

export default Figure