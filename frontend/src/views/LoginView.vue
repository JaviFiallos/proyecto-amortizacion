<template>
  <div class="auth-page">
    <div class="auth-bg"></div>
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">🏦</div>
        <h1>Bienvenido</h1>
        <p>Ingresa tus credenciales para continuar</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="doLogin">
        <el-form-item label="Correo electrónico" prop="email">
          <el-input v-model="form.email" type="email" prefix-icon="Message" placeholder="usuario@email.com" size="large" />
        </el-form-item>
        <el-form-item label="Contraseña" prop="password">
          <el-input v-model="form.password" type="password" prefix-icon="Lock" show-password size="large" placeholder="••••••••" @keyup.enter="doLogin" />
        </el-form-item>

        <el-button type="primary" size="large" :loading="loading" class="submit-btn" @click="doLogin">
          Iniciar sesión
        </el-button>
      </el-form>

      <div class="auth-footer">
        <span>¿No tienes cuenta?</span>
        <RouterLink to="/register">Regístrate aquí</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()
const loading = ref(false)
const formRef = ref()

const form = reactive({ email: '', password: '' })
const rules = {
  email: [{ required: true, message: 'Ingresa tu correo', trigger: 'blur' }],
  password: [{ required: true, message: 'Ingresa tu contraseña', trigger: 'blur' }],
}

async function doLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.login(form.email, form.password)
      toast.success('¡Bienvenido!')
      router.push(authStore.isAdmin ? '/admin' : '/client')
    } catch {
      toast.error('Credenciales incorrectas')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.auth-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f2540 0%, #1a3c5e 50%, #2575bc 100%);
}

.auth-bg::before {
  content: '';
  position: absolute;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%);
  top: -200px; right: -200px;
  border-radius: 50%;
}

.auth-bg::after {
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(37,117,188,0.2) 0%, transparent 70%);
  bottom: -100px; left: -100px;
  border-radius: 50%;
}

.auth-card {
  position: relative;
  z-index: 1;
  background: rgba(255,255,255,0.97);
  border-radius: 20px;
  padding: 48px 40px;
  width: 420px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.35);
  backdrop-filter: blur(20px);
  animation: slideUp 0.4s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

.auth-header { text-align: center; margin-bottom: 32px; }
.auth-logo { font-size: 3.2rem; margin-bottom: 12px; }
.auth-header h1 { font-size: 1.8rem; font-weight: 800; color: #1a3c5e; margin-bottom: 8px; }
.auth-header p  { color: #64748b; font-size: 0.95rem; }

.submit-btn { width: 100%; margin-top: 8px; border-radius: 10px !important; height: 46px; font-size: 1rem; font-weight: 600; }

.auth-footer { text-align: center; margin-top: 24px; font-size: 0.9rem; color: #64748b; }
.auth-footer a { color: #2575bc; font-weight: 600; text-decoration: none; margin-left: 6px; }
.auth-footer a:hover { text-decoration: underline; }
</style>
