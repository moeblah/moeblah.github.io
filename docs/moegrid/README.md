---
title: Moe Docs
lang: en-US
---
# Hello Moe Grid

## JavaScript Data Grid: Get Start with Moe Grid

Moe Grid is the industry standard for javaScript Enterprise Applications. Developers using Moe Grid are building
applications that would not be possible if Moe Grid did not exist.

```javascript
const columns = [
  { field: "make" },
  { field: "model" },
  { field: "price" }
]

// specify the data
const data = [ 
  { make: "Samsung", model: "S21", price: 800 },
  { make: "Apple", model: "IPhone12", price: 1000 },
  { make: "Xiaomi", model: "MI11", price: 1100 }
]

// let the grid know which columns and what data to use
const gridOptions = {
  columns: columns,
  data: data
}

// set the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', () => {
  const gridDiv = document.querySelector('#myGrid')
  new moe.Grid(gridDiv, gridOptions)
})
```