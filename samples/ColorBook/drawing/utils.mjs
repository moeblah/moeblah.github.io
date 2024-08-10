
export function hexToRgbArray(hex) {
  hex = hex.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)
  return [r, g, b]
}

export function arrayToHex(...rgb) {
  return `#${rgb.map(x => {
    const hex = x.toString(16)
    return hex.length === 1 ? "0" + hex : hex
  }).join('')}`
}


const utils = {
  hexToRgbArray: hexToRgbArray,
  arrayToHex: arrayToHex,
}

export default utils
