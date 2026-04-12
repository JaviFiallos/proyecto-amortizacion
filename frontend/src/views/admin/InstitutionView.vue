<template>
  <div>
    <div class="page-header">
      <h2>🏢 Configuración de la Institución</h2>
      <p>Personaliza la información y el logo de tu institución financiera</p>
    </div>

    <el-row :gutter="24">
      <!-- Formulario -->
      <el-col :span="16">
        <el-card>
          <template #header><span style="font-weight:600">Información General</span></template>
          <el-form ref="formRef" :model="form" label-position="top" v-loading="saving">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="Nombre de la Institución" prop="name">
                  <el-input v-model="form.name" placeholder="Cooperativa XYZ" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Slogan">
                  <el-input v-model="form.slogan" placeholder="Tu aliado financiero" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="RUC">
                  <el-input v-model="form.ruc" placeholder="1790000000001" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Teléfono">
                  <el-input v-model="form.phone" placeholder="(03) 2800-000" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Correo">
                  <el-input v-model="form.email" placeholder="info@institucion.fin.ec" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Sitio Web">
                  <el-input v-model="form.website" placeholder="https://www.institucion.fin.ec" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="Dirección">
                  <el-input v-model="form.address" placeholder="Av. Principal 123, Ciudad" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="Descripción">
                  <el-input v-model="form.description" type="textarea" :rows="3" placeholder="Breve descripción de la institución..." />
                </el-form-item>
              </el-col>
            </el-row>
            <el-button type="primary" :icon="Check" @click="save">Guardar cambios</el-button>
          </el-form>
        </el-card>
      </el-col>

      <!-- Logo -->
      <el-col :span="8">
        <el-card>
          <template #header><span style="font-weight:600">Logo</span></template>
          <div class="logo-preview">
            <img v-if="logoPreview || institution?.logo_path" :src="logoPreview || `http://localhost:8000/${institution?.logo_path}`" alt="Logo" class="logo-img" />
            <div v-else class="logo-placeholder">
              <el-icon :size="48" color="#94a3b8"><Picture /></el-icon>
              <p>Sin logo</p>
            </div>
          </div>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept="image/png,image/jpeg,image/svg+xml"
            :on-change="onLogoChange"
          >
            <el-button :icon="Upload" style="width:100%;margin-top:12px">Seleccionar imagen</el-button>
          </el-upload>
          <el-button v-if="logoFile" type="success" :icon="Check" style="width:100%;margin-top:8px" @click="uploadLogo">
            Subir logo
          </el-button>
        </el-card>

        <!-- Vista previa de la tarjeta -->
        <el-card style="margin-top:16px">
          <template #header><span style="font-weight:600">Vista Previa</span></template>
          <div class="preview-card">
            <div class="preview-logo">{{ form.name?.charAt(0) || '?' }}</div>
            <div class="preview-name">{{ form.name || 'Nombre de la institución' }}</div>
            <div class="preview-slogan">{{ form.slogan || 'Slogan institucional' }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useInstitutionStore } from '@/stores/institution'
import { institutionApi } from '@/api'
import { useToast } from 'vue-toastification'
import { Check, Upload } from '@element-plus/icons-vue'

const store = useInstitutionStore()
const toast = useToast()
const saving = ref(false)
const logoFile = ref<File | null>(null)
const logoPreview = ref<string | null>(null)
const formRef = ref()
const institution = computed(() => store.institution)

const form = reactive({
  name: '', slogan: '', ruc: '', phone: '', email: '', website: '', address: '', description: '',
})

onMounted(async () => {
  await store.fetch()
  if (store.institution) Object.assign(form, store.institution)
})

async function save() {
  saving.value = true
  try {
    if (store.institution) await store.update(form)
    else await store.create(form)
    toast.success('Institución actualizada correctamente')
  } catch { toast.error('Error al guardar') }
  finally { saving.value = false }
}

function onLogoChange(file: any) {
  logoFile.value = file.raw
  logoPreview.value = URL.createObjectURL(file.raw)
}

async function uploadLogo() {
  if (!logoFile.value) return
  try {
    await institutionApi.uploadLogo(logoFile.value)
    await store.fetch()
    toast.success('Logo actualizado')
    logoFile.value = null
    logoPreview.value = null
  } catch { toast.error('Error al subir el logo') }
}
</script>

<style scoped>
.logo-preview { display: flex; align-items: center; justify-content: center; min-height: 140px; border: 2px dashed #e2e8f0; border-radius: 12px; overflow: hidden; }
.logo-img { max-width: 100%; max-height: 140px; object-fit: contain; }
.logo-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; color: #94a3b8; }
.preview-card { text-align: center; padding: 16px; background: linear-gradient(135deg,#1a3c5e,#2575bc); border-radius: 12px; }
.preview-logo { width: 52px; height: 52px; border-radius: 50%; background: rgba(255,255,255,0.15); color: #fff; font-size: 1.4rem; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; }
.preview-name { color: #fff; font-weight: 700; font-size: 1rem; }
.preview-slogan { color: #38bdf8; font-size: 0.8rem; margin-top: 4px; }
</style>
