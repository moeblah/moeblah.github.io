import DrawTool from "./DrawTool.mjs"
import {arrayToHex, hexToRgbArray} from "./utils.mjs"

class Fill extends DrawTool {
  #color = [0, 0, 0]
  #opacity = 1

  startDrawing(context, x, y, sourceContext) {
    this.floodFill(context, x, y, sourceContext)
  }

  set color(value){
    this.#color = hexToRgbArray(value)
  }

  get color(){
    return arrayToHex(...this.#color)
  }

  set opacity(value){
    console.log('vluae', value)
    this.#opacity = value
  }

  get opacity(){
    return this.#opacity
  }

  floodFill(context, x, y, sourceContext) {
    const width = sourceContext.canvas.width
    const height = sourceContext.canvas.height
    const imageData = context.getImageData(0, 0, width, height)
    const sourceImageData = sourceContext.getImageData(0, 0, width, height).data
    const visited = new Uint8ClampedArray(width*height)
    visited.fill(0)

    const stack = [[x, y]]
    const baseColor = this.getPixel(sourceImageData, x, y, width)

    if (this.colorsMatch(baseColor, this.#color)) return
    while (stack.length) {
      const [cx, cy] = stack.pop()
      const index = cy * width + cx
      if (visited[index]) continue

      const currentColor = this.getPixel(sourceImageData, cx, cy, width)

      visited[index] = 1
      if (this.colorDistance(baseColor, currentColor) < 110) {
        const color = [...this.#color, Math.round(this.#opacity * 255)]
        // const blendColors =  this.blendColors(baseColor, color, 0.5)
        this.setPixel(imageData.data, cx, cy, width, color)
        if (cx > 0) stack.push([cx - 1, cy])
        if (cx < width - 1) stack.push([cx + 1, cy])
        if (cy > 0) stack.push([cx, cy - 1])
        if (cy < height - 1) stack.push([cx, cy + 1])
      }
    }
    context.putImageData(imageData, 0, 0)
  }

  getPixel(imageData, x, y, width) {
    const index = (y * width + x) * 4
    return [imageData[index], imageData[index + 1], imageData[index + 2], imageData[index + 3]]
  }

  setPixel(imageData, x, y, width, color) {
      const index = (y * width + x) * 4
      imageData[index] = color[0]
      imageData[index + 1] = color[1]
      imageData[index + 2] = color[2]
      imageData[index + 3] = color[3]
  }


  blendColors(color1, color2, alpha) {
    return [
      Math.round(color1[0] * (1 - alpha) + color2[0] * alpha),
      Math.round(color1[1] * (1 - alpha) + color2[1] * alpha),
      Math.round(color1[2] * (1 - alpha) + color2[2] * alpha),
      Math.round(color1[3] * (1 - alpha) + color2[3] * alpha)
    ];
  }

  colorsMatch(color1, color2) {
    return color1[0] === color2[0] &&
      color1[1] === color2[1] &&
      color1[2] === color2[2] &&
      color1[3] === color2[3]
  }

  colorDistance(color1, color2) {
    const rDiff = color1[0] - color2[0];
    const gDiff = color1[1] - color2[1];
    const bDiff = color1[2] - color2[2];
    const aDiff = color1[3] - color2[3];
    return Math.sqrt(rDiff * rDiff + gDiff * gDiff + bDiff * bDiff + aDiff * aDiff);
  }
}


export default Fill