export function helloWorld(selector: any): void{
    const el = document.querySelector(selector) as HTMLElement;
    el.innerHTML = "<div>Hello World!!</div>";
}
