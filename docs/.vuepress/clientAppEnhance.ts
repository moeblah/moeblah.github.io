import { defineClientAppEnhance } from '@vuepress/client';
import { defineAsyncComponent } from 'vue'


export default defineClientAppEnhance(({ app, router, siteData }) => {
    app.component(
        'hello-world',
        defineAsyncComponent(() => import('./components/hello.vue'))
    );
    app.component(
        'moegrid-hello',
        defineAsyncComponent(() => import('./components/moegrid/hello.vue'))
    );
})