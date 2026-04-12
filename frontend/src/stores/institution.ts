import { defineStore } from 'pinia'
import { ref } from 'vue'
import { institutionApi } from '@/api'
import type { Institution } from '@/types'

export const useInstitutionStore = defineStore('institution', () => {
    const institution = ref<Institution | null>(null)

    async function fetch() {
        try {
            const { data } = await institutionApi.get()
            institution.value = data
        } catch {
            institution.value = null
        }
    }

    async function update(payload: Partial<Institution>) {
        const { data } = await institutionApi.update(payload)
        institution.value = data
    }

    async function create(payload: Partial<Institution>) {
        const { data } = await institutionApi.create(payload)
        institution.value = data
    }

    return { institution, fetch, update, create }
})
