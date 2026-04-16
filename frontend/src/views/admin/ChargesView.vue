<template>
  <div>
    <div class="page-header">
      <h2>➕ Cobros Indirectos</h2>
      <p>Administra los seguros, donaciones y cobros adicionales por tipo de crédito</p>
    </div>

    <el-row :gutter="20" style="margin-bottom:16px">
      <el-col :span="8">
        <el-select v-model="selectedTypeId" placeholder="Filtrar por tipo de crédito" style="width:100%" clearable @change="load">
          <el-option v-for="t in creditTypes" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-button type="primary" :icon="Plus" @click="openModal()">Nuevo cobro</el-button>
      </el-col>
    </el-row>

    <el-card>
      <el-table :data="charges" v-loading="loading" stripe>
        <el-table-column prop="name" label="Nombre" min-width="160" />
        <el-table-column label="Tipo" width="160">
          <template #default="{ row }">
            <el-tag>{{ chargeTypeLabel(row.charge_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Valor" width="130" align="right">
          <template #default="{ row }">
            <strong style="color:#2575bc">{{ row.is_percentage ? row.value.toFixed(3)+'%' : '$'+row.value.toFixed(2) }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="Frecuencia" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_monthly ? '' : 'warning'">{{ row.is_monthly ? 'Mensual' : 'Única vez' }}</el-tag>
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

    <!-- Modal -->
    <el-dialog v-model="showModal" :title="editing ? 'Editar cobro' : 'Nuevo cobro indirecto'" width="480px">
      <el-form :model="form" label-position="top">
        <el-form-item label="Tipo de crédito">
          <el-select v-model="form.credit_type_id" style="width:100%">
            <el-option v-for="t in creditTypes" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Nombre del cobro">
          <el-input v-model="form.name" placeholder="Seguro de desgravamen" />
        </el-form-item>
        <el-form-item label="Tipo de cobro">
          <el-select v-model="form.charge_type" style="width:100%">
            <el-option v-for="c in chargeTypes" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Valor">
              <el-input-number v-model="form.value" :min="0" :precision="4" :step="0.01" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Tipo de valor">
              <el-radio-group v-model="form.is_percentage">
                <el-radio :value="true">% del monto</el-radio>
                <el-radio :value="false">USD fijo</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Frecuencia">
          <el-radio-group v-model="form.is_monthly">
            <el-radio :value="true">Mensual (cada período)</el-radio>
            <el-radio :value="false">Una sola vez</el-radio>
          </el-radio-group>
        </el-form-item>
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
import type { CreditType, IndirectCharge } from '@/types'

const toast = useToast()
const creditTypes = ref<CreditType[]>([])
const charges = ref<IndirectCharge[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<number | null>(null)
const selectedTypeId = ref<number | undefined>()

const chargeTypes = [
  { label: 'Seguro de desgravamen', value: 'seguro_desgravamen' },
  { label: 'Aporte SOLCA', value: 'aporte_solca' },
  { label: 'Comisión administrativa', value: 'comision_administrativa' },
  { label: 'Donación a fundación', value: 'donacion' },
  { label: 'Otro', value: 'otro' },
]
const chargeTypeLabel = (v: string) => chargeTypes.find(x=>x.value===v)?.label || v

const form = reactive({ name:'', charge_type:'seguro_desgravamen', value:0.06, is_percentage:true, is_monthly:true, credit_type_id:0 })

async function load() {
  loading.value = true
  try {
    creditTypes.value = (await creditApi.listTypes()).data
    charges.value = (await creditApi.listCharges(selectedTypeId.value)).data
    if (!form.credit_type_id && creditTypes.value.length) form.credit_type_id = creditTypes.value[0]!.id
  } finally { loading.value = false }
}
onMounted(load)

function openModal(row?: IndirectCharge) {
  editing.value = row?.id || null
  if (row) Object.assign(form, row)
  else Object.assign(form, { name:'', charge_type:'seguro_desgravamen', value:0.06, is_percentage:true, is_monthly:true, credit_type_id: creditTypes.value[0]?.id || 0 })
  showModal.value = true
}

async function submit() {
  saving.value = true
  try {
    if (editing.value) await creditApi.updateCharge(editing.value, form)
    else await creditApi.createCharge(form)
    toast.success(editing.value ? 'Cobro actualizado' : 'Cobro creado')
    showModal.value = false
    await load()
  } catch { toast.error('Error al guardar') }
  finally { saving.value = false }
}

async function remove(id: number) {
  await ElMessageBox.confirm('¿Eliminar este cobro?', 'Confirmar', { type:'warning' })
  await creditApi.deleteCharge(id)
  toast.success('Eliminado')
  await load()
}
</script>
