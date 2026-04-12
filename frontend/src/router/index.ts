import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guest: true },
    },

    // ── Admin ──────────────────────────────────────────
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        { path: '', redirect: '/admin/institution' },
        { path: 'institution', name: 'admin-institution', component: () => import('@/views/admin/InstitutionView.vue') },
        { path: 'credit-types', name: 'admin-credit-types', component: () => import('@/views/admin/CreditTypesView.vue') },
        { path: 'charges', name: 'admin-charges', component: () => import('@/views/admin/ChargesView.vue') },
        { path: 'investment-types', name: 'admin-investment-types', component: () => import('@/views/admin/InvestmentTypesView.vue') },
        { path: 'applications', name: 'admin-applications', component: () => import('@/views/admin/ApplicationsView.vue') },
      ],
    },

    // ── Cliente ────────────────────────────────────────
    {
      path: '/client',
      component: () => import('@/layouts/ClientLayout.vue'),
      meta: { requiresAuth: true, role: 'client' },
      children: [
        { path: '', redirect: '/client/amortization' },
        { path: 'amortization', name: 'client-amortization', component: () => import('@/views/client/AmortizationView.vue') },
        { path: 'investment', name: 'client-investment', component: () => import('@/views/client/InvestmentView.vue') },
        { path: 'investment/apply', name: 'client-invest-apply', component: () => import('@/views/client/InvestmentApplyView.vue') },
      ],
    },

    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

// Guards de navegación
router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return next(auth.isAdmin ? '/admin' : '/client')
  }
  if (to.meta.role === 'admin' && !auth.isAdmin) {
    return next('/client')
  }
  if (to.meta.role === 'client' && !auth.isClient) {
    return next('/admin')
  }
  next()
})

export default router
