import { defineClientAppEnhance } from '@vuepress/client';
import {defineAsyncComponent, defineComponent} from 'vue'


export default defineClientAppEnhance(({ app, router, siteData }) => {
    app.component(
        'hello-world',
        defineAsyncComponent(() => import('./components/hello.vue'))
    );
    app.component(
        'moegrid-get-started',
        defineAsyncComponent(() => import('./components/moegrid/get-started.vue'))
    );
})