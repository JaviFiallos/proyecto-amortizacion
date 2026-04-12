<template>
  <div>
    <div class="page-header">
      <h2>📈 Simulador de Inversiones</h2>
      <p>Calcula el rendimiento de tu certificado de Depósito a Plazo Fijo (DPF).</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="10">
        <el-card>
          <template #header><span style="font-weight:600">Simular DPF</span></template>
          <el-form label-position="top" @submit.prevent="simulate">
            <el-form-item label="Producto de inversión">
              <el-select v-model="form.investment_type_id" style="width:100%" @change="onTypeChange">
                <el-option v-for="t in types" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
              <div v-if="selectedType" style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                Tasa referencial: <strong>{{ selectedType.annual_rate }}%</strong> |
                Plazo: {{ selectedType.min_term_days }} - {{ selectedType.max_term_days }} días
              </div>
            </el-form-item>

            <el-form-item label="Monto a invertir (USD)">
              <el-input-number v-model="form.amount" :min="selectedType?.min_amount || 100" :max="selectedType?.max_amount || 100000" style="width:100%" size="large" />
            </el-form-item>

            <el-form-item label="Plazo (días)">
              <el-input-number v-model="form.term_days" :min="selectedType?.min_term_days || 30" :max="selectedType?.max_term_days || 360" style="width:100%" size="large" />
            </el-form-item>

            <el-button type="primary" size="large" style="width:100%;margin-top:10px" :loading="loading" @click="simulate">
              Simular Rendimiento
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card v-loading="loading">
          <template #header><span style="font-weight:600">Proyección de Inversión</span></template>
          
          <div v-if="!result" class="empty-state">
            <el-icon :size="48" color="#cbd5e1"><TrendCharts /></el-icon>
            <p>Ingresa los datos para ver la proyección</p>
          </div>

          <div v-else>
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="stat-card">
                  <div class="stat-label">Inversión Inicial</div>
                  <div class="stat-value">${{ result.amount.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="stat-card">
                  <div class="stat-label">Total al Vencimiento</div>
                  <div class="stat-value" style="color:#10b981">${{ result.total_at_maturity.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</div>
                </div>
              </el-col>
            </el-row>

            <div class="details-box">
              <div class="detail-row">
                <span>Tasa de Interés Anual:</span>
                <strong>{{ result.annual_rate }}%</strong>
              </div>
              <div class="detail-row">
                <span>Interés Bruto Generado:</span>
                <strong style="color:var(--primary-light)">+ ${{ result.gross_interest.toLocaleString('es-EC',{minimumFractionDigits:2}) }}</strong>
              </div>
              <div class="detail-row text-danger">
                <span>Retención IR (Impuesto):</span>
                <strong>- ${{ result.ir_retention.toLocaleString('es-EC',{minimumFractionDigits:2}) }}</strong>
              </div>
              <div class="detail-row total-interest">
                <span>Interés Neto a Recibir:</span>
                <strong>${{ result.net_interest.toLocaleString('es-EC',{minimumFractionDigits:2}) }}</strong>
              </div>
            </div>

            <el-button type="success" :icon="Download" style="width:100%" :loading="downloading" @click="downloadPdf">
              Descargar PDF de Simulación
            </el-button>
            <el-button type="primary" plain style="width:100%;margin-top:12px;margin-left:0" @click="$router.push('/client/investment/apply')">
              Invertir Ahora en Línea
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { investmentApi } from '@/api'
import { useToast } from 'vue-toastification'
import { TrendCharts, Download } from '@element-plus/icons-vue'
import type { InvestmentType, InvestmentResult } from '@/types'

const toast = useToast()
const types = ref<InvestmentType[]>([])
const loading = ref(false)
const downloading = ref(false)
const result = ref<InvestmentResult | null>(null)

const form = reactive({
  investment_type_id: null as number | null,
  amount: 10000,
  term_days: 90
})

const selectedType = computed(() => types.value.find(t => t.id === form.investment_type_id))

onMounted(async () => {
  try {
    const { data } = await investmentApi.listTypes()
    types.value = data.filter((t: InvestmentType) => t.is_active)
    if (types.value.length > 0) form.investment_type_id = types.value[0].id
  } catch {
    toast.error('Error al cargar tipos de inversión')
  }
})

function onTypeChange() {
  if (!selectedType.value) return
  if (form.amount < (selectedType.value.min_amount || 0)) form.amount = selectedType.value.min_amount || 0
  if (form.term_days < selectedType.value.min_term_days) form.term_days = selectedType.value.min_term_days
  if (form.term_days > selectedType.value.max_term_days) form.term_days = selectedType.value.max_term_days
}

async function simulate() {
  if (!form.investment_type_id) return toast.warning('Seleccione un producto')
  loading.value = true
  try {
    const { data } = await investmentApi.simulate(form)
    result.value = data
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Error en la simulación')
  } finally {
    loading.value = false
  }
}

async function downloadPdf() {
  if (!result.value?.simulation_id) return
  downloading.value = true
  try {
    const response = await investmentApi.downloadPdf(result.value.simulation_id)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `simulacion_dpf_${new Date().getTime()}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch {
    toast.error('Error al generar PDF')
  } finally {
    downloading.value = false
  }
}
</script>

<style scoped>
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 0; color: #64748b; text-align: center; }
.empty-state p { margin-top: 12px; font-size: 0.95rem; }

.details-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius);
  padding: 20px;
  margin: 20px 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 0.95rem;
  border-bottom: 1px dashed #cbd5e1;
}
.detail-row:last-child { border-bottom: none; }
.text-danger { color: #ef4444; }

.total-interest {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 2px solid #e2e8f0;
  font-size: 1.1rem;
  color: #10b981;
}
</style>
