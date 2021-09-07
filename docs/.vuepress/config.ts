import { defineUserConfig } from "vuepress";
import type { DefaultThemeOptions } from "vuepress";

export default defineUserConfig<DefaultThemeOptions>({
    base: '/',
    lang: 'en-US',
    title: "Moe Page",
    description: '',
    themeConfig: {
        darkMode: true,
        navbar: [
            {text: 'Home', link: '/'},
        ]
    },
    markdown: {
    }
})