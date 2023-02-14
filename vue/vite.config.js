import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { createHtmlPlugin } from 'vite-plugin-html';

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: '../gui',
    emptyOutDir: true,
  },
  plugins: [
    vue(),
    createHtmlPlugin({
      minify: true,
      inject: {
        data: {
          title: 'index',
          //injectScript: '<script src="/eel.js"></script>',
          injectScript:
            '<script src="http://localhost:8083/eel.js"></script><script>window.eel.set_host("ws://localhost:8083");</script>',
        },
      },
    }),
  ],
});
