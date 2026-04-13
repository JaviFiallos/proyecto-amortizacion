<template>
  <el-container class="client-shell">
    <!-- Top nav -->
    <el-header class="client-nav">
      <div class="nav-brand">
        <span class="nav-logo">🏦</span>
        <div class="nav-titles">
          <span class="nav-name">{{ institution?.name || 'Simulador Financiero' }}</span>
          <span class="nav-slogan">{{ institution?.slogan || 'Tu aliado financiero' }}</span>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        :ellipsis="false"
        background-color="transparent"
        text-color="#cbd5e1"
        active-text-color="#38bdf8"
        router
        class="nav-menu"
      >
        <el-menu-item index="/client/amortization">
          <el-icon><Money /></el-icon> Simulador de Crédito
        </el-menu-item>
        <el-menu-item index="/client/investment">
          <el-icon><TrendCharts /></el-icon> Simulador de Inversión
        </el-menu-item>
        <el-menu-item index="/client/investment/apply">
          <el-icon><Document /></el-icon> Invertir en Línea
        </el-menu-item>
        <el-menu-item index="/client/profile">
          <el-icon><UserFilled /></el-icon>
          Mi Perfil
          <el-badge v-if="!authStore.user?.is_kyc_verified" value="!" type="danger" style="margin-left:6px" />
        </el-menu-item>
      </el-menu>

      <div class="nav-user">
        <el-avatar :size="34" class="user-avatar">
          {{ authStore.user?.name?.charAt(0).toUpperCase() }}
        </el-avatar>
        <span class="user-name">{{ authStore.user?.name }}</span>
        <el-button type="danger" size="small" text @click="doLogout">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </el-header>

    <!-- Content -->
    <el-main class="client-content">
      <transition name="slide-up" mode="out-in">
        <RouterView :key="$route.path" />
      </transition>
    </el-main>

    <!-- Footer -->
    <el-footer class="client-footer" height="48px">
      <span>{{ institution?.name || 'Simulador Financiero' }} © {{ new Date().getFullYear() }} — Valores referenciales</span>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useInstitutionStore } from '@/stores/institution'
import { SwitchButton, UserFilled } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const institutionStore = useInstitutionStore()
const institution = computed(() => institutionStore.institution)
const route = useRoute()
const router = useRouter()
const activeMenu = computed(() => route.path)
function doLogout() { authStore.logout(); router.push('/login') }
</script>

<style scoped>
.client-shell { min-height: 100vh; display: flex; flex-direction: column; }

.client-nav {
  background: linear-gradient(135deg, #1a3c5e 0%, #2575bc 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px !important;
  box-shadow: 0 4px 20px rgba(26,60,94,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.nav-logo { font-size: 1.8rem; }
.nav-titles { display: flex; flex-direction: column; }
.nav-name { font-size: 1rem; font-weight: 700; color: #fff; }
.nav-slogan { font-size: 0.72rem; color: #38bdf8; letter-spacing: 0.05em; }

.nav-menu {
  border: none !important;
  flex: 1;
  justify-content: center;
}
.nav-menu :deep(.el-menu-item) {
  border-bottom: none !important;
  border-radius: 8px;
  margin: 0 4px;
  transition: all 0.2s;
}
.nav-menu :deep(.el-menu-item:hover),
.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(56,189,248,0.12) !important;
  color: #38bdf8 !important;
}

.nav-user { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.user-avatar { background: rgba(255,255,255,0.2); color: #fff; font-weight: 700; }
.user-name { font-size: 0.9rem; color: #cbd5e1; }

.client-content { background: #f0f4f8; padding: 32px; flex: 1; }

.client-footer {
  background: #1a3c5e;
  color: #94a3b8;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
