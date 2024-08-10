import Outline from "./Outline.mjs"
import Layer from "./Layer.mjs"


class Canvas{
  constructor(canvasEl) {
    this.element = canvasEl
    this.width = this.element.width
    this.height = this.element.height
    this.context = this.element.getContext('2d')

    this.outline = null
    this.layers = []
    this.addLayer()
    this.selectedLayer = this.layers.at(-1)
    // this.selectedLayer = document.getElementById('colorCanvas').getContext('2d')

    this.element.addEventListener('mousedown', (e)=>this.startDrawing(e))
    this.element.addEventListener('mousemove', (e)=>this.draw(e))
    document.addEventListener('mouseup', (e)=>this.endDrawing(e))

    this.element.addEventListener('touchstart', (e)=>{
      e.preventDefault()
      e.stopPropagation()
      this.startDrawing(e)
    }, { passive: false })
    this.element.addEventListener('touchmove', (e)=>{
      e.preventDefault()
      e.stopPropagation()
      this.draw(e)
    }, { passive: false })
    document.addEventListener('touchend', (e)=>{
      e.preventDefault()
      e.stopPropagation()
      this.endDrawing(e)
    }, { passive: false })

    this.isDrawing = false
    setInterval(()=>{this.render()}, 1000/60)
  }

  createContext(){
    const canvasEl = document.createElement('canvas')
    canvasEl.width = this.width
    canvasEl.height = this.height
    return canvasEl.getContext('2d', { willReadFrequently: true })
  }

  reset(){
    this.layers = []
    this.outline = null
    this.addLayer()
    this.selectedLayer = this.layers.at(-1)
  }

  addLayer(){
    this.layers.push(new Layer(this.width, this.height))
  }

  selectLayer(index){
    this.selectedLayer = this.layers[index]
  }

  setOutline(path) {
    Outline.createFromImage(path).then(figure => {
      this.outline = this.createContext()
      figure.transform({width: this.width, height: this.height})
      this.outline.putImageData(figure.imageData, 0, 0)
    })
  }

  unsetOutline() {
    this.outline = null
  }

  setDrawTool(tool){
    this.drawTool = tool
  }

  startDrawing(e){
    const {x, y} = this.getCoordinates(e)
    const sourceContext = this.outline || this.selectedLayer.context
    this.drawTool.startDrawing(this.selectedLayer.createFigure(), x, y, sourceContext)
    this.isDrawing = true
  }

  endDrawing(e){
    const {x, y} = this.getCoordinates(e)
    const sourceContext = this.outline || this.selectedLayer.context
    this.drawTool.endDrawing(this.selectedLayer.lastFigure, x, y, sourceContext)
    this.isDrawing = false
  }

  draw(e){
    if (this.isDrawing) {
      const {x, y} = this.getCoordinates(e)
      const sourceContext = this.outline || this.selectedLayer.context
      this.drawTool.draw(this.selectedLayer.lastFigure, x, y, sourceContext)
    }
  }

  getCoordinates(e) {
    if (e.touches && e.touches.length > 0) {
      const touch = e.touches[0]
      const rect = this.element.getBoundingClientRect()
      return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top
      }
    } else {
      return {
        x: e.offsetX,
        y: e.offsetY
      }
    }
  }

  render(){
    this.context.clearRect(0, 0, this.width, this.height)
    this.layers[0].updateImageData()
    this.context.drawImage(this.layers[0].canvas, 0, 0)
    if (this.outline) this.context.drawImage(this.outline.canvas, 0, 0)
  }
}

export default Canvas