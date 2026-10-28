import {defineConfig} from 'vite';
export default defineConfig({server:{proxy:{'/api':{target:'http://127.0.0.1:8080',changeOrigin:false}}},test:{environment:'jsdom',setupFiles:['./src/test-setup.js'],testTimeout:30000}});
