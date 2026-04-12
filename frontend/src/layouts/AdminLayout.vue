<template>
  <el-container class="admin-shell">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="sidebar-logo" @click="toggleCollapse">
        <div class="logo-icon">🏦</div>
        <transition name="fade">
          <div v-if="!isCollapsed" class="logo-text">
            <span class="logo-name">{{ institution?.name || 'Admin' }}</span>
            <span class="logo-role">Administrador</span>
          </div>
        </transition>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        background-color="#1a3c5e"
        text-color="#cbd5e1"
        active-text-color="#38bdf8"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/admin/institution">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>Institución</template>
        </el-menu-item>
        <el-menu-item index="/admin/credit-types">
          <el-icon><Money /></el-icon>
          <template #title>Tipos de Crédito</template>
        </el-menu-item>
        <el-menu-item index="/admin/charges">
          <el-icon><Plus /></el-icon>
          <template #title>Cobros Indirectos</template>
        </el-menu-item>
        <el-menu-item index="/admin/investment-types">
          <el-icon><TrendCharts /></el-icon>
          <template #title>Tipos de Inversión</template>
        </el-menu-item>
        <el-menu-item index="/admin/applications">
          <el-icon><Document /></el-icon>
          <template #title>Solicitudes</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button type="danger" :icon="SwitchButton" text @click="doLogout">
          <span v-if="!isCollapsed">Cerrar sesión</span>
        </el-button>
      </div>
    </el-aside>

    <!-- Main -->
    <el-container class="main-container">
      <el-header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" @click="toggleCollapse"><Fold /></el-icon>
          <span class="breadcrumb">{{ routeTitle }}</span>
        </div>
        <div class="topbar-right">
          <el-avatar :size="36" class="user-avatar">
            {{ authStore.user?.name?.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="user-name">{{ authStore.user?.name }}</span>
        </div>
      </el-header>

      <el-main class="content-area">
        <transition name="slide-up" mode="out-in">
          <RouterView :key="$route.path" />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useInstitutionStore } from '@/stores/institution'
import { SwitchButton, Fold } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const institutionStore = useInstitutionStore()
const institution = computed(() => institutionStore.institution)
const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '220px')
const activeMenu = computed(() => route.path)

const titleMap: Record<string, string> = {
  '/admin/institution': 'Configuración de Institución',
  '/admin/credit-types': 'Tipos de Crédito',
  '/admin/charges': 'Cobros Indirectos',
  '/admin/investment-types': 'Tipos de Inversión',
  '/admin/applications': 'Solicitudes de Inversión',
}
const routeTitle = computed(() => titleMap[route.path] || 'Panel Admin')

function toggleCollapse() { isCollapsed.value = !isCollapsed.value }
function doLogout() { authStore.logout(); router.push('/login') }
</script>

<style scoped>
.admin-shell { height: 100vh; overflow: hidden; }

.sidebar {
  background: #1a3c5e;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease;
  overflow: hidden;
  box-shadow: 4px 0 20px rgba(0,0,0,0.15);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  cursor: pointer;
  min-height: 72px;
}

.logo-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-role {
  font-size: 0.72rem;
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.sidebar-menu {
  border: none !important;
  flex: 1;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-menu-item.is-active) {
  background: rgba(56, 189, 248, 0.12) !important;
  border-right: 3px solid #38bdf8;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.sidebar-footer .el-button {
  width: 100%;
  justify-content: center;
}

/* Topbar */
.topbar {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 8px rgba(0,0,0,0.06);
  height: 60px !important;
}

.topbar-left { display: flex; align-items: center; gap: 12px; }
.collapse-btn { font-size: 1.2rem; cursor: pointer; color: #64748b; transition: color 0.2s; }
.collapse-btn:hover { color: #1a3c5e; }
.breadcrumb { font-weight: 600; color: #1e293b; font-size: 0.95rem; }

.topbar-right { display: flex; align-items: center; gap: 10px; }
.user-avatar { background: #1a3c5e; color: #fff; font-weight: 700; }
.user-name { font-size: 0.9rem; font-weight: 500; color: #1e293b; }

.main-container { overflow: hidden; }
.content-area { background: #f0f4f8; overflow-y: auto; padding: 28px; }
</style>
