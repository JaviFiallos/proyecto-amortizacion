import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
    const token = ref<string | null>(localStorage.getItem('access_token'))

    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')
    const isClient = computed(() => user.value?.role === 'client')

    async function login(email: string, password: string) {
        const { data } = await authApi.login({ email, password })
        token.value = data.access_token
        user.value = data.user
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
    }

    async function register(payload: { name: string; email: string; password: string; role?: string }) {
        await authApi.register(payload)
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
    }

    async function refreshUser() {
        try {
            const { data } = await authApi.me()
            user.value = data
            localStorage.setItem('user', JSON.stringify(data))
        } catch { /* silently fail */ }
    }

    return { user, token, isAuthenticated, isAdmin, isClient, login, register, logout, refreshUser }
})
