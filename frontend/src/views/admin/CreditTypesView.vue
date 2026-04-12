<template>
  <div>
    <div class="page-header">
      <h2>💳 Tipos de Crédito</h2>
      <p>Configura los tipos de crédito disponibles y sus tasas de interés</p>
    </div>

    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">Lista de tipos de crédito</span>
          <el-button type="primary" :icon="Plus" @click="openModal()">Nuevo tipo</el-button>
        </div>
      </template>

      <el-table :data="types" v-loading="loading" stripe style="width:100%">
        <el-table-column prop="name" label="Nombre" min-width="180" />
        <el-table-column prop="category" label="Categoría" width="140">
          <template #default="{ row }">
            <el-tag :type="categoryColor(row.category)" class="category-tag">{{ categoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nominal_rate" label="Tasa Nominal" width="130" align="right">
          <template #default="{ row }"><strong style="color:#2575bc">{{ row.nominal_rate.toFixed(2) }}%</strong></template>
        </el-table-column>
        <el-table-column prop="max_term_months" label="Plazo Máx." width="120" align="center">
          <template #default="{ row }">{{ row.max_term_months ? row.max_term_months + ' meses' : '—' }}</template>
        </el-table-column>
        <el-table-column label="Estado" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? 'Activo' : 'Inactivo' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Cobros" width="90" align="center">
          <template #default="{ row }">
            <el-badge :value="row.indirect_charges?.length || 0" type="warning" />
          </template>
        </el-table-column>
        <el-table-column label="" width="120" align="right">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" circle @click="openModal(row)" />
            <el-button size="small" type="danger" :icon="Delete" circle @click="remove(row.id)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Modal -->
    <el-dialog v-model="showModal" :title="editing ? 'Editar tipo de crédito' : 'Nuevo tipo de crédito'" width="520px">
      <el-form :model="form" label-position="top" ref="formRef">
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="Nombre" prop="name" :rules="[{required:true,message:'Campo requerido'}]">
              <el-input v-model="form.name" placeholder="Crédito de Consumo" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Categoría">
              <el-select v-model="form.category" style="width:100%">
                <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Tasa Nominal Anual (%)">
              <el-input-number v-model="form.nominal_rate" :min="0" :max="50" :precision="2" :step="0.5" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Plazo máximo (meses)">
              <el-input-number v-model="form.max_term_months" :min="1" :max="360" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Estado">
              <el-switch v-model="form.is_active" active-text="Activo" inactive-text="Inactivo" />
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
import { creditApi } from '@/api'
import { useToast } from 'vue-toastification'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { CreditType } from '@/types'

const toast = useToast()
const types = ref<CreditType[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<number | null>(null)
const formRef = ref()

const categories = [
  { label: 'Consumo', value: 'consumo' },
  { label: 'Hipotecario', value: 'hipotecario' },
  { label: 'Educación', value: 'educacion' },
  { label: 'Microcrédito', value: 'microcredito' },
  { label: 'Productivo', value: 'productivo' },
]
const categoryColor = (c: string) => ({ consumo:'', hipotecario:'success', educacion:'warning', microcredito:'danger', productivo:'info' }[c] || '')
const categoryLabel = (c: string) => categories.find(x=>x.value===c)?.label || c

const form = reactive({ name:'', category:'consumo', nominal_rate:12.0, max_term_months:60, min_amount:100, max_amount:50000, is_active:true })

async function load() {
  loading.value = true
  try { types.value = (await creditApi.listTypes()).data } finally { loading.value = false }
}
onMounted(load)

function openModal(row?: CreditType) {
  editing.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { name:'', category:'consumo', nominal_rate:12.0, max_term_months:60, min_amount:100, max_amount:50000, is_active:true })
  showModal.value = true
}

async function submit() {
  saving.value = true
  try {
    if (editing.value) await creditApi.updateType(editing.value, form)
    else await creditApi.createType(form)
    toast.success(editing.value ? 'Tipo actualizado' : 'Tipo creado')
    showModal.value = false
    await load()
  } catch { toast.error('Error al guardar') }
  finally { saving.value = false }
}

async function remove(id: number) {
  await ElMessageBox.confirm('¿Eliminar este tipo de crédito?', 'Confirmar', { type:'warning' })
  await creditApi.deleteType(id)
  toast.success('Eliminado')
  await load()
}
</script>
