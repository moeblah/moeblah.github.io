class Layer{

  constructor(width, height) {
    this.context = document.createElement('canvas').getContext('2d')
    this.context.canvas.width = width
    this.context.canvas.height = height
    this.figures = []
  }

  get width(){
    return this.context.canvas.width
  }

  get height(){
    return this.context.canvas.height
  }

  get imageData(){
    return this.context.getImageData(0,0, this.width, this.height).data
  }

  get canvas(){
    return this.context.canvas
  }

  get lastFigure(){
    return this.figures.at(-1)
  }

  createFigure(){
    const figure = document.createElement('canvas').getContext('2d')
    figure.canvas.width = this.width
    figure.canvas.height = this.height
    this.figures.push(figure)
    return figure
  }


  pushFigure(figure){
    this.figures.push(figure)
    this.updateImageData()
  }

  updateImageData(){
    this.context.clearRect(0, 0, this.width, this.height)
    for (const figure of this.figures) this.context.drawImage(figure.canvas, 0, 0)
  }
}

export default Layer