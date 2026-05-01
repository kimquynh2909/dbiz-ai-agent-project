import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { getProxyOptions } from 'frappe-ui/src/utils/vite-dev-server'
import { webserver_port } from '../../../sites/common_site_config.json'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/ai-agent/',
  plugins: [vue()],
  server: {
    port: 8080,
    cors: {
      origin: ['http://127.0.0.1:8800', 'http://localhost:8800'],
      credentials: true,
    },
    proxy: getProxyOptions({ port: webserver_port }),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),

    },
  },
  build: {
    outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
    emptyOutDir: true,
    target: 'es2020',
    manifest: true,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    }
  },
  optimizeDeps: {
    include: ['frappe-ui > feather-icons', 'showdown', 'engine.io-client'],
  },
  define: {
    // Vue feature flags
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
    // Vue i18n feature flags
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
})
