import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElIcons from '@element-plus/icons-vue'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

// Registrar todos los iconos de Element Plus globalmente
for (const [key, component] of Object.entries(ElIcons)) {
    app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(Toast, {
    position: 'top-right',
    timeout: 3500,
    closeOnClick: true,
    pauseOnHover: true,
})

app.mount('#app')
