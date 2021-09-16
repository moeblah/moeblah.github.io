export function hello(selector: string): void{
    const el = document.querySelector(selector) as HTMLElement;
    el.innerHTML = "<div>Hello MoeGrid!!</div>";
}

class Column {
    name: string;
    field: string;
}

class gridOptions {

}


class MoeGrid {
    constructor() {
    }
}
