import { defineClientAppEnhance } from '@vuepress/client';
import { defineAsyncComponent } from 'vue'


export default defineClientAppEnhance(({ app, router, siteData }) => {
    app.component(
        'hello',
        defineAsyncComponent(() => import('./components/hello.vue'))
    );
})