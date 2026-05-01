import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

// Import language files
import vi from './locales/vi.json'
import en from './locales/en.json'

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'vi',
  fallbackLocale: 'en',
  globalInjection: true,
  messages: {
    vi,
    en
  }
})

// Create Pinia store
const pinia = createPinia()

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

// Socket.IO removed

app.use(router)
app.use(pinia)
app.use(i18n)
app.use(resourcesPlugin)

app.component('Button', Button)
app.mount('#app')
