import Figure from "./Figure.mjs"

class Outline extends Figure{
  constructor(...args) {
    super(...args)
    this.#transformImageData()
  }

  #transformImageData(){
    const data = this.source.data
    for (let i = 0; i < data.length;){
      const [r, g, b, a] =[i++, i++, i++, i++]
      const outlineGrayScale = (data[r] * 0.21 + data[g] * 0.72 + data[b] * 0.07) * (data[a] / 255)
      data[r] = 0
      data[g] = 0
      data[b] = 0
      data[a] = 255 - outlineGrayScale
    }
  }
}

export default Outline