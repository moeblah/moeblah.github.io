import Figure from "./Figure.mjs"
import DrawTool from "./DrawTool.mjs"
import Fill from "./Fill.mjs";
import JsYaml from "../libs/js-yaml.mjs"
import {hexToRgbArray, arrayToHex} from "./utils.mjs"

/**
 * brush.yaml
 *
 * ```yaml
 * patterns:
 *   - "01.png:
 *   - "02.png"
 * defaultOptions:
 *   size: 20
 *   opacity: 1
 *   force: 0.5
 *
 * ```
 *
 */

class Axis{
  x = 0
  y = 0

  constructor(x, y) {
    this.x = x
    this.y = y
  }

  distance(point){
    return Math.sqrt((point.x - this.x) ** 2 + (point.y - this.y) ** 2)
  }

  radians(point){
    return Math.atan2(point.y - this.y, point.x - this.x)
  }
}

class BrushImage{
  #source = null
  #width = 0
  #height = 0
  #size = 0
  #color = [0, 0, 0]
  #angle = 0
  #radians = 0

  constructor(source) {
    this.canvas = null
    this.#source = null

    Figure.createFromImage(source).then(figure=>{
      this.#width = figure.width
      this.#height = figure.height
      this.#size = this.#size? this.#size: figure.width > figure.height? figure.width: figure.height
      this.#source = figure
      this.#createCanvas()
    })
  }

  #createCanvas(){
    if (!this.#source) return

    const originWidth = this.#source.sourceWidth
    const originHeight = this.#source.sourceHeight
    const scale  = originWidth > originHeight? this.size / originWidth: this.size / originHeight

    const width = originWidth * scale
    const height = originHeight * scale
    const radians = this.angle * (Math.PI / 180)

    this.#source.transform({width:width, height:height, radians: radians})

    const imageData = this.#source.imageData
    for (let i = 0; i < this.#source.imageData.data.length;) {
      const [r, g, b, a] = [i++, i++, i++, i++]
      const alpha = (imageData.data[r] * 0.21 + imageData.data[g] * 0.72 + imageData.data[b] * 0.07) * (imageData.data[a] / 255)
      imageData.data[r] = this.#color[0]
      imageData.data[g] = this.#color[1]
      imageData.data[b] = this.#color[2]
      imageData.data[a] = 255 - alpha
    }

    const context = document.createElement("canvas").getContext('2d')
    context.canvas.width = this.#source.width
    context.canvas.height = this.#source.height
    this.#width = this.#source.width
    this.#height = this.#source.height

    context.putImageData(this.#source.imageData, 0, 0)
    this.canvas = context.canvas
  }

  set color(value){
    this.#color = typeof(value) === "string"? hexToRgbArray(value): value
    this.#createCanvas()
  }

  get color(){
    return arrayToHex(this.#color)
  }

  /**
   * 브러시 패턴의 사이즈를 변경한다. 높이와 너비중 더 큰쪽을 사이즈의 기준으로 정한다.
   * @param value
   */
  set size(value){
    this.#size = value
    if (!this.#source) return
    this.#createCanvas()
  }

  get size(){
    return this.#size
  }

  set angle(value){
    this.#angle = value
    this.#radians = this.#angle * (Math.PI / 180)
    this.#createCanvas()
  }

  get angle(){
    return this.#angle
  }

  get width(){
    return this.#width
  }

  get height(){
    return this.#height
  }
}


class Brush extends DrawTool{
  #images = []
  #color = [0, 0, 0]
  #size = 1       // 0.01 ~ 2.00   default 1.00   브러시 사이즈 비율
  #angle = 0      // 0 ~ 360
  spacing = 1     // 0.01 ~ 2.00   default 1.00   브러시 간격 비율
  opacity = 1   // 0.01 ~ 1.00
  force = 0.5       // 0.01 ~ 1.00   default 1.00   필압
  useBoundary = false

  #originBrushContext = document.createElement('canvas').getContext('2d')
  #brushContext = document.createElement('canvas').getContext('2d')
  #maskContext = document.createElement('canvas').getContext('2d')

  constructor() {
    super()
  }

  get color(){
    return arrayToHex(this.#color)
  }

  set color(value){
    this.#color = value
    for(const image of this.#images) image.color = this.#color
  }

  get size(){
    return this.#size
  }

  set size(value){
    this.#size = value
    for(const image of this.#images) image.size = this.#size
  }

  get angle(){
    return this.#angle
  }

  set angle(value){
    this.#angle = value
    for(const image of this.#images) image.angle = this.#angle
  }

  setCanvasSize(canvas, width, height){
    canvas.width = width
    canvas.height = height
  }

  startDrawing(context, x, y, sourceContext) {
    const {width, height} = context.canvas

    this.setCanvasSize(this.#originBrushContext.canvas, width, height)
    this.setCanvasSize(this.#brushContext.canvas, width, height)
    this.setCanvasSize(this.#maskContext.canvas, width, height)

    this.#originBrushContext.clearRect(0, 0, width, height)
    this.#brushContext.clearRect(0, 0, width, height)
    this.#maskContext.clearRect(0, 0, width, height)
    console.log(this.useBoundary)
    if (this.useBoundary) {
      new Fill().startDrawing(this.#maskContext, x, y, sourceContext)
    } else {
      this.#maskContext.fillStyle = 'black';
      this.#maskContext.fillRect(0, 0, width, height); // 흰색 배경
    }

    this.#originBrushContext.drawImage(context.canvas, 0, 0)

    this.#brushContext.imageSmoothingEnabled = true
    this.#brushContext.imageSmoothingQuality = 'high'
    this.#brushContext.globalCompositeOperation = 'source-over'

    this.#brushContext.globalAlpha = this.force


    this.drawBrush(context, x, y)
    this.lastAxis = new Axis(x, y)
    this.lastDraw = new Axis(x, y)
  }

  endDrawing(context, x, y) {
  }

  draw(context, x, y) {
    const axis = new Axis(x, y)
    const radians = this.lastAxis.radians(axis)
    const distance = this.lastAxis.distance(axis)

    for (let i = 0; i < distance; i+=0.1) {
      const progress = new Axis(
        this.lastAxis.x + Math.cos(radians) * (i),
        this.lastAxis.y + Math.sin(radians) * (i)
      )

      if (
        Math.abs((progress.x - this.lastDraw.x)) >= this.lastImage.width * this.spacing ||
        Math.abs((progress.y - this.lastDraw.y)) >= this.lastImage.height * this.spacing
      ){
        this.lastDraw = progress
        this.drawBrush(context, progress.x, progress.y)
      }
    }

    this.lastAxis.x = x
    this.lastAxis.y = y
  }

  drawBrush(context , x, y){
    const image = this.#images[0];
    // 브러시 컨텍스트에 이미지 그리기
    // this.#brushContext.clearRect(0, 0, this.#brushContext.canvas.width, this.#brushContext.canvas.height);
    this.#brushContext.drawImage(image.canvas, x - image.width / 2, y - image.height / 2);

    // 마스크 적용을 위한 임시 캔버스에 마스킹 처리
    const tempContext = document.createElement('canvas').getContext('2d');
    tempContext.canvas.width = context.canvas.width;
    tempContext.canvas.height = context.canvas.height;

    // tempContext에 마스크 적용
    tempContext.drawImage(this.#maskContext.canvas, 0, 0); // 마스크 이미지를 그리기
    tempContext.globalCompositeOperation = 'source-in'; // 'source-in'을 사용하여 마스크 영역에만 그리기
    tempContext.drawImage(this.#brushContext.canvas, 0, 0); // 브러시 이미지를 마스크된 영역에 그리기
    tempContext.globalCompositeOperation = 'source-over'; // 'source-in'을 사용하여 마스크 영역에만 그리기

    // 결과를 메인 context에 그리기
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);
    context.globalAlpha = 1;
    context.drawImage(this.#originBrushContext.canvas, 0, 0);
    context.globalAlpha = this.opacity;
    context.drawImage(tempContext.canvas, 0, 0); // 마스크가 적용된 tempCanvas를 context에 그리기

    this.lastImage = image;
  }

  loadBrushFile(path){
    const http = new XMLHttpRequest()
    http.open('GET', path, false)
    http.send()

    if(http.status === 200){
      return JsYaml.load(http.responseText)
    } else {
      return null
    }
  }

  setBrush(path){
    const brushPath = `${path}/brush.yaml`
    const brushSetting = {defaultOptions:{}, ...this.loadBrushFile(brushPath)}
    this.clearBrushImage()
    for(const imageName of brushSetting.images){
      this.pushBrushImage(`${path}/${imageName}`)
    }
    this.size = brushSetting.defaultOptions.size
    this.spacing = brushSetting.defaultOptions.spacing
    this.force = brushSetting.defaultOptions.force
    this.opacity = brushSetting.defaultOptions.opacity
    this.angle = brushSetting.defaultOptions.angle
  }

  clearBrushImage(){
    this.#images = []
  }

  pushBrushImage(path){
    const brushImage = new BrushImage(path)
    brushImage.size = this.size
    brushImage.color = this.#color
    this.#images.push(brushImage)
  }

  popBrushImage(){
    return this.#images.pop()
  }
}

export default Brush