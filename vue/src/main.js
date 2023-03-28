import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import 'vuetify/styles';

import App from './App.vue';
import './assets/main.css';

const pinia = createPinia();

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'darkTheme',
    themes: {
      darkTheme: {
        dark: true,
        colors: {
          surface: '#333333',
          primary: '#03DAC6',
          error: '#B00020',
        },
      },
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  defaults: {
    global: {
      ripple: false,
    },
    VBtn: {
      variant: 'outlined',
    },
    VAutocomplete: {
      variant: 'outlined',
      color: 'primary',
    },
    VTextField: {
      variant: 'outlined',
      color: 'primary',
    },
  },
});

const app = createApp(App);

app.config.globalProperties.$eel = window['eel'];
app.use(pinia);
app.use(vuetify);
app.mount('#app');
