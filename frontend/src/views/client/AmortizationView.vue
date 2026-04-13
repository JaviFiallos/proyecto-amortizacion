<template>
  <div>
    <div class="page-header">
      <h2>📊 Simulador de Crédito</h2>
      <p>Calcula las cuotas de tu préstamo de acuerdo al sistema de amortización que prefieras.</p>
    </div>

    <el-row :gutter="24">
      <!-- Formulario -->
      <el-col :span="8">
        <el-card>
          <template #header><span style="font-weight:600">Datos del Crédito</span></template>
          <el-form label-position="top" @submit.prevent="simulate">
            <el-form-item label="Tipo de crédito">
              <el-select v-model="form.credit_type_id" style="width:100%" @change="onCreditTypeChange">
                <el-option v-for="t in creditTypes" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
              <div v-if="selectedType" style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                Tasa nominal: <strong>{{ selectedType.nominal_rate }}%</strong> |
                Plazo máx: {{ selectedType.max_term_months || 'N/A' }} meses
              </div>
            </el-form-item>
            
            <el-form-item label="Monto a solicitar (USD)">
              <el-input-number v-model="form.amount" :min="100" :step="100" style="width:100%" size="large" />
            </el-form-item>

            <el-form-item label="Plazo (meses)">
              <el-input-number v-model="form.term_months" :min="1" :max="selectedType?.max_term_months || 360" style="width:100%" size="large" />
            </el-form-item>

            <el-form-item label="Sistema de amortización">
              <el-radio-group v-model="form.system">
                <el-radio value="frances">Francés (Cuota Fija)</el-radio>
                <el-radio value="aleman">Alemán (Cuota Variable)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-button type="primary" size="large" style="width:100%;margin-top:10px" :loading="loading" @click="simulate">
              Calcular Tabla
            </el-button>
          </el-form>
        </el-card>

        <el-card v-if="result" style="margin-top: 16px;">
          <template #header><span style="font-weight:600">Resumen</span></template>
          <div class="summary-item">
            <span>Capital Neto:</span>
            <strong>${{ result.total_capital.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</strong>
          </div>
          <div class="summary-item">
            <span>Total Interés:</span>
            <strong>${{ result.total_interest.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</strong>
          </div>
          <div class="summary-item">
            <span>Cobros Indirectos:</span>
            <strong>${{ result.total_charges.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</strong>
          </div>
          <div class="summary-item total">
            <span>Total a Pagar:</span>
            <strong style="color:var(--primary)">${{ result.total_payment.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</strong>
          </div>

          <el-button type="success" :icon="Download" style="width:100%;margin-top:16px" :loading="downloading" @click="downloadPdf">
            Descargar PDF
          </el-button>
        </el-card>
      </el-col>

      <!-- Tabla de resultados -->
      <el-col :span="16">
        <el-card v-loading="loading">
          <template #header><span style="font-weight:600">Tabla de Amortización</span></template>
          
          <div v-if="!result" class="empty-state">
            <el-icon :size="48" color="#cbd5e1"><Money /></el-icon>
            <p>Ingresa los datos y haz clic en "Calcular Tabla"</p>
          </div>

          <div v-else style="overflow-x: auto;">
            <table class="amort-table">
              <thead>
                <tr>
                  <th>Mes</th>
                  <th>Saldo Inicial</th>
                  <th>Capital</th>
                  <th>Interés</th>
                  <th v-for="name in result.charge_names" :key="name">{{ name }}</th>
                  <th>Cuota Total</th>
                  <th>Saldo Final</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in result.schedule" :key="row.period">
                  <td>{{ row.period }}</td>
                  <td>${{ row.initial_balance.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                  <td>${{ row.capital.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                  <td>${{ row.interest.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                  <td v-for="name in result.charge_names" :key="name">
                    ${{ (row.indirect_charges[name] || 0).toLocaleString('es-EC', {minimumFractionDigits:2}) }}
                  </td>
                  <td style="font-weight:600;color:var(--primary-light)">
                    ${{ row.total_payment.toLocaleString('es-EC', {minimumFractionDigits:2}) }}
                  </td>
                  <td>${{ row.final_balance.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                </tr>
                <tr class="total-row">
                  <td colspan="2">TOTALES</td>
                  <td>${{ result.total_capital.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                  <td>${{ result.total_interest.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                  <td v-for="name in result.charge_names" :key="name">
                    ${{ (result.total_charges_details[name] || 0).toLocaleString('es-EC', {minimumFractionDigits:2}) }}
                  </td>
                  <td>${{ result.total_payment.toLocaleString('es-EC', {minimumFractionDigits:2}) }}</td>
                  <td>-</td>
                </tr>
              </tbody>
            </table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { creditApi, amortizationApi } from '@/api'
import { useToast } from 'vue-toastification'
import { Money, Download } from '@element-plus/icons-vue'
import type { CreditType, AmortizationResult } from '@/types'

const toast = useToast()
const creditTypes = ref<CreditType[]>([])
const loading = ref(false)
const downloading = ref(false)
const result = ref<AmortizationResult | null>(null)

const form = reactive({
  credit_type_id: null as number | null,
  amount: 5000,
  term_months: 12,
  system: 'frances'
})

const selectedType = computed(() => creditTypes.value.find(t => t.id === form.credit_type_id))

onMounted(async () => {
  try {
    const { data } = await creditApi.listTypes()
    creditTypes.value = data.filter((t: CreditType) => t.is_active)
    if (creditTypes.value.length > 0) {
      form.credit_type_id = creditTypes.value[0].id
    }
  } catch {
    toast.error('Error al cargar tipos de crédito')
  }
})

function onCreditTypeChange() {
  if (selectedType.value && form.term_months > (selectedType.value.max_term_months || 360)) {
    form.term_months = selectedType.value.max_term_months || 360
  }
}

async function simulate() {
  if (!form.credit_type_id) {
    toast.warning('Seleccione un tipo de crédito')
    return
  }
  loading.value = true
  try {
    const { data } = await amortizationApi.calculate(form)
    result.value = data
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Error en el cálculo')
  } finally {
    loading.value = false
  }
}

async function downloadPdf() {
  if (!result.value?.schedule_id) return
  downloading.value = true
  try {
    const response = await amortizationApi.downloadPdf(result.value.schedule_id)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `amortizacion_${form.system}_${new Date().getTime()}.pdf`)
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
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #64748b;
  text-align: center;
}
.empty-state p { margin-top: 12px; font-size: 0.95rem; }

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.95rem;
}
.summary-item:last-child { border-bottom: none; }
.summary-item.total {
  font-size: 1.1rem;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 2px solid #e2e8f0;
}
</style>
