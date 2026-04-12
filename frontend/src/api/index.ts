import api from './axios'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { name: string; email: string; password: string; role?: string; cedula?: string; phone?: string }

export const authApi = {
    login: (data: LoginPayload) => api.post('/api/auth/login', data),
    register: (data: RegisterPayload) => api.post('/api/auth/register', data),
    me: () => api.get('/api/auth/me'),
}

export const institutionApi = {
    get: () => api.get('/api/institution/'),
    create: (data: object) => api.post('/api/institution/', data),
    update: (data: object) => api.put('/api/institution/', data),
    uploadLogo: (file: File) => {
        const form = new FormData()
        form.append('file', file)
        return api.post('/api/institution/logo', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    },
}

export const creditApi = {
    listTypes: () => api.get('/api/credits/types'),
    getType: (id: number) => api.get(`/api/credits/types/${id}`),
    createType: (data: object) => api.post('/api/credits/types', data),
    updateType: (id: number, data: object) => api.put(`/api/credits/types/${id}`, data),
    deleteType: (id: number) => api.delete(`/api/credits/types/${id}`),
    listCharges: (creditTypeId?: number) => api.get('/api/credits/charges', { params: { credit_type_id: creditTypeId } }),
    createCharge: (data: object) => api.post('/api/credits/charges', data),
    updateCharge: (id: number, data: object) => api.put(`/api/credits/charges/${id}`, data),
    deleteCharge: (id: number) => api.delete(`/api/credits/charges/${id}`),
}

export const amortizationApi = {
    preview: (data: object) => api.post('/api/amortization/calculate/preview', data),
    calculate: (data: object) => api.post('/api/amortization/calculate', data),
    downloadPdf: (scheduleId: number) => api.post(`/api/amortization/pdf/${scheduleId}`, {}, { responseType: 'blob' }),
    history: () => api.get('/api/amortization/history'),
}

export const investmentApi = {
    listTypes: () => api.get('/api/investments/types'),
    createType: (data: object) => api.post('/api/investments/types', data),
    updateType: (id: number, data: object) => api.put(`/api/investments/types/${id}`, data),
    deleteType: (id: number) => api.delete(`/api/investments/types/${id}`),
    preview: (data: object) => api.post('/api/investments/simulate/preview', data),
    simulate: (data: object) => api.post('/api/investments/simulate', data),
    comparative: (typeId: number, amount: number) =>
        api.get(`/api/investments/simulate/comparative/${typeId}`, { params: { amount } }),
    downloadPdf: (simId: number) => api.post(`/api/investments/simulate/pdf/${simId}`, {}, { responseType: 'blob' }),
    createApplication: (data: object) => api.post('/api/investments/apply', data),
    myApplications: () => api.get('/api/investments/applications'),
    allApplications: () => api.get('/api/investments/applications/all'),
    updateAppStatus: (appId: number, status: string) =>
        api.put(`/api/investments/applications/${appId}/status`, null, { params: { status } }),
    uploadDocument: (appId: number, docType: string, file: File) => {
        const form = new FormData()
        form.append('doc_type', docType)
        form.append('file', file)
        return api.post(`/api/investments/applications/${appId}/documents`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },
    uploadBiometric: (appId: number, blob: Blob) => {
        const form = new FormData()
        form.append('file', blob, 'selfie.jpg')
        return api.post(`/api/investments/applications/${appId}/biometric`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },
}
