<template>
  <div>
    <div class="page-header">
      <h2>📈 Tipos de Inversión</h2>
      <p>Configura los productos de inversión (DPF) disponibles para los clientes</p>
    </div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">Productos de inversión</span>
          <el-button type="primary" :icon="Plus" @click="openModal()">Nuevo producto</el-button>
        </div>
      </template>
      <el-table :data="types" v-loading="loading" stripe>
        <el-table-column prop="name" label="Nombre" min-width="200" />
        <el-table-column prop="annual_rate" label="Tasa Anual" width="120" align="right">
          <template #default="{ row }"><strong style="color:#10b981">{{ row.annual_rate.toFixed(2) }}%</strong></template>
        </el-table-column>
        <el-table-column label="Plazo" width="160" align="center">
          <template #default="{ row }">{{ row.min_term_days }} – {{ row.max_term_days }} días</template>
        </el-table-column>
        <el-table-column label="Modalidad" width="150" align="center">
          <template #default="{ row }">
            <el-tag type="success">{{ row.payment_mode === 'al_vencimiento' ? 'Al vencimiento' : 'Mensual' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="100" align="right">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" circle @click="openModal(row)" />
            <el-button size="small" type="danger" :icon="Delete" circle @click="remove(row.id)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showModal" :title="editing ? 'Editar producto' : 'Nuevo tipo de inversión'" width="500px">
      <el-form :model="form" label-position="top">
        <el-form-item label="Nombre del producto">
          <el-input v-model="form.name" placeholder="Depósito a Plazo Fijo" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Tasa anual (%)">
              <el-input-number v-model="form.annual_rate" :min="0" :max="20" :precision="2" :step="0.25" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Modalidad de pago">
              <el-select v-model="form.payment_mode" style="width:100%">
                <el-option label="Al vencimiento" value="al_vencimiento" />
                <el-option label="Mensual" value="mensual" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Plazo mínimo (días)">
              <el-input-number v-model="form.min_term_days" :min="1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Plazo máximo (días)">
              <el-input-number v-model="form.max_term_days" :min="1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Monto mínimo (USD)">
              <el-input-number v-model="form.min_amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Monto máximo (USD)">
              <el-input-number v-model="form.max_amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showModal=false">Cancelar</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ editing ? 'Actualizar' : 'Crear' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { investmentApi } from '@/api'
import { useToast } from 'vue-toastification'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { InvestmentType } from '@/types'

const toast = useToast()
const types = ref<InvestmentType[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<number | null>(null)

const form = reactive({ name:'', annual_rate:7.0, min_term_days:30, max_term_days:720, min_amount:500, max_amount:100000, payment_mode:'al_vencimiento' })

async function load() {
  loading.value = true
  try { types.value = (await investmentApi.listTypes()).data } finally { loading.value = false }
}
onMounted(load)

function openModal(row?: InvestmentType) {
  editing.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { name:'', annual_rate:7.0, min_term_days:30, max_term_days:720, min_amount:500, max_amount:100000, payment_mode:'al_vencimiento' })
  showModal.value = true
}

async function submit() {
  saving.value = true
  try {
    if (editing.value) await investmentApi.updateType(editing.value, form)
    else await investmentApi.createType(form)
    toast.success(editing.value ? 'Actualizado' : 'Producto creado')
    showModal.value = false; await load()
  } catch { toast.error('Error al guardar') }
  finally { saving.value = false }
}

async function remove(id: number) {
  await ElMessageBox.confirm('¿Eliminar este tipo de inversión?','Confirmar',{type:'warning'})
  await investmentApi.deleteType(id)
  toast.success('Eliminado'); await load()
}
</script>
