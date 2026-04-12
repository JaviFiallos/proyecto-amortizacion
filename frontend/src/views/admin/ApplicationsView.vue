<template>
  <div>
    <div class="page-header">
      <h2>📋 Solicitudes de Inversión</h2>
      <p>Gestiona y aprueba las solicitudes de inversión en línea de los clientes</p>
    </div>
    <el-card>
      <el-table :data="apps" v-loading="loading" stripe>
        <el-table-column prop="id" label="N°" width="70" align="center" />
        <el-table-column prop="amount" label="Monto" width="130" align="right">
          <template #default="{ row }">$ {{ row.amount.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</template>
        </el-table-column>
        <el-table-column prop="term_days" label="Plazo" width="100" align="center">
          <template #default="{ row }">{{ row.term_days }} días</template>
        </el-table-column>
        <el-table-column label="Estado" width="180" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Biométrica" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="row.biometric_status==='verificado' ? 'success' : 'warning'">
              {{ row.biometric_status === 'verificado' ? '✅ Verificado' : '⏳ Pendiente' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Fecha" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="Acciones" width="220" align="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="updateStatus(row.id,'aprobado')" :disabled="row.status==='aprobado'">Aprobar</el-button>
            <el-button size="small" type="danger" @click="updateStatus(row.id,'rechazado')" :disabled="row.status==='rechazado'">Rechazar</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { investmentApi } from '@/api'
import { useToast } from 'vue-toastification'
import type { InvestmentApplication } from '@/types'

const toast = useToast()
const apps = ref<InvestmentApplication[]>([])
const loading = ref(false)

const statusColors: Record<string,string> = { pendiente:'warning', documentos_enviados:'', biometria_verificada:'info', aprobado:'success', rechazado:'danger' }
const statusLabels: Record<string,string> = { pendiente:'Pendiente', documentos_enviados:'Docs enviados', biometria_verificada:'Biométrica OK', aprobado:'Aprobada', rechazado:'Rechazada' }
const statusColor = (s: string) => statusColors[s] || ''
const statusLabel = (s: string) => statusLabels[s] || s
const formatDate = (d?: string) => d ? new Date(d).toLocaleDateString('es-EC') : '—'

async function load() {
  loading.value = true
  try { apps.value = (await investmentApi.allApplications()).data } finally { loading.value = false }
}
onMounted(load)

async function updateStatus(id: number, status: string) {
  await investmentApi.updateAppStatus(id, status)
  toast.success(`Solicitud ${status}`)
  await load()
}
</script>
