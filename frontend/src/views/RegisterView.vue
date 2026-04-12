<template>
  <div class="auth-page">
    <div class="auth-bg"></div>
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">🏦</div>
        <h1>Crear cuenta</h1>
        <p>Completa el formulario para registrarte</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="doRegister">
        <el-form-item label="Nombre completo" prop="name">
          <el-input v-model="form.name" prefix-icon="User" placeholder="Juan Pérez" size="large" />
        </el-form-item>
        <el-form-item label="Correo electrónico" prop="email">
          <el-input v-model="form.email" type="email" prefix-icon="Message" placeholder="usuario@email.com" size="large" />
        </el-form-item>
        <el-form-item label="Contraseña" prop="password">
          <el-input v-model="form.password" type="password" prefix-icon="Lock" show-password size="large" placeholder="••••••••" />
        </el-form-item>
        <el-form-item label="Tipo de cuenta" prop="role">
          <el-select v-model="form.role" size="large" style="width:100%">
            <el-option label="Cliente" value="client" />
            <el-option label="Administrador" value="admin" />
          </el-select>
        </el-form-item>

        <el-button type="primary" size="large" :loading="loading" class="submit-btn" @click="doRegister">
          Crear cuenta
        </el-button>
      </el-form>

      <div class="auth-footer">
        <span>¿Ya tienes cuenta?</span>
        <RouterLink to="/login">Inicia sesión</RouterLink>
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

const form = reactive({ name: '', email: '', password: '', role: 'client' })
const rules = {
  name: [{ required: true, message: 'Ingresa tu nombre', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: 'Correo inválido', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: 'Mínimo 6 caracteres', trigger: 'blur' }],
}

async function doRegister() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.register(form)
      await authStore.login(form.email, form.password)
      toast.success('¡Cuenta creada exitosamente!')
      router.push(authStore.isAdmin ? '/admin' : '/client')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error al registrar')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.auth-bg { position: absolute; inset: 0; background: linear-gradient(135deg, #0f2540 0%, #1a3c5e 50%, #2575bc 100%); }
.auth-bg::before { content: ''; position: absolute; width: 600px; height: 600px; background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%); top: -200px; right: -200px; border-radius: 50%; }
.auth-card { position: relative; z-index: 1; background: rgba(255,255,255,0.97); border-radius: 20px; padding: 48px 40px; width: 420px; box-shadow: 0 24px 80px rgba(0,0,0,0.35); animation: slideUp 0.4s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-logo { font-size: 3.2rem; margin-bottom: 12px; }
.auth-header h1 { font-size: 1.8rem; font-weight: 800; color: #1a3c5e; margin-bottom: 8px; }
.auth-header p { color: #64748b; font-size: 0.95rem; }
.submit-btn { width: 100%; margin-top: 8px; border-radius: 10px !important; height: 46px; font-size: 1rem; font-weight: 600; }
.auth-footer { text-align: center; margin-top: 24px; font-size: 0.9rem; color: #64748b; }
.auth-footer a { color: #2575bc; font-weight: 600; text-decoration: none; margin-left: 6px; }
</style>
