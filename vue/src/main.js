import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

import './assets/main.css';

const pinia = createPinia();
const app = createApp(App);

app.config.globalProperties.$eel = window['eel'];
app.use(pinia);
app.mount('#app');
