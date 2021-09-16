
function querySelector(selector: string, el?: HTMLElement|Document): HTMLElement{
    el = el === undefined? document: el;
    return el.querySelector(selector) as HTMLElement
}

function createElement(tagName: string, options?:ElementCreationOptions): HTMLElement{
    return document.createElement(tagName, options) as HTMLElement;
}

class Header {

}

class Body {

}


class Footer {

}

class Column {
    name: string
    field: string;
}


class gridOptions {

}


class MoeGrid {
    private readonly container: HTMLDivElement;
    private readonly viewPort: HTMLDivElement;

    constructor(private readonly selector: string) {
        this.container = querySelector(selector) as HTMLDivElement;
        this.viewPort = createElement('div') as HTMLDivElement;
        this.viewPort.innerHTML = "This is MoeGrid";
        this.container.appendChild(this.viewPort);
    }
}


export function moeGrid(selector: string): MoeGrid{
    return new MoeGrid(selector);
}

