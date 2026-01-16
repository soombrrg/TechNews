import './assets/main.css'
import 'vue-toastification/dist/index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast, { POSITION, type PluginOptions } from 'vue-toastification'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// Toast configuration
const toastOptions: PluginOptions = {
  position: POSITION.TOP_RIGHT,
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false,
  maxToasts: 3,
  newestOnTop: true,
  transition: 'Vue-Toastification__fade',
}

app.use(pinia)
app.use(router)
app.use(Toast, toastOptions)

app.mount('#app')
