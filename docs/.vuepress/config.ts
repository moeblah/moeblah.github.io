import { defineUserConfig } from "vuepress";
import type { DefaultThemeOptions } from "vuepress";

const { path } = require('@vuepress/utils');

console.log('component : ' + path.resolve(__dirname, './components/hello.vue'));

export default defineUserConfig<DefaultThemeOptions>({
    lang: 'en-US',
    title: "Moe Page",
    description: '',
    debug: false,
    themeConfig: {
        darkMode: true,
        navbar: [
            {text: 'Home', link: '/'},
            {text: 'History', link: '/history/'},
            {text: 'MoeGrid', link: '/moegrid/'},
        ],
        sidebar: {
            '/history/': [
                {
                    text: 'History',
                    children: [
                        {text: 'Install Node.js on Ubuntu', link: 'install_node_js_on_ubuntu.md'},
                        {text: 'Create VuePress project', link: 'create_vuepress_project.md'},
                        {text: 'Deploy VuePress to GitHub page', link: 'deploy_vuepress_to_github_page.md'},
                        {text: 'Authentication to GitHub', link: 'authentication_to_github.md'},
                        {text: 'Install docker on Ubuntu 20.04', link: 'install_docker_on_ubuntu_20_04.md'},
                        {text: 'Create docker image for Vuepress', link: 'create_docker_image_for_vuepress.md'},
                    ],
                },
            ],
            '/moegrid/': [
                {
                    text: 'History',
                    children: [
                        {text: 'Prepare To Develop', link: 'prepare_to_develop.md'},
                        {text: 'Getting Started', link: 'getting_started.md'},
                    ],
                },
            ],
        },
        markdown: {
        },
        // plugins: [
        //     [
        //         '@vuepress/register-components',
        //         {
        //             components: {
        //                 hello: path.resolve(__dirname, './components/hello.vue')
        //             },
        //         },
        //     ],
        // ],
    },
})