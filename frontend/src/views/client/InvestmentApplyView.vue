<template>
  <div class="apply-container">
    <div class="page-header">
      <h2>🚀 Invertir en Línea</h2>
      <p>Abre tu Depósito a Plazo Fijo sin salir de casa mediante nuestro proceso 100% digital.</p>
    </div>

    <el-card class="stepper-card">
      <el-steps :active="activeStep" finish-status="success" align-center style="margin-bottom: 30px;">
        <el-step title="Datos Inversión" icon="TrendCharts" />
        <el-step title="Documentos" icon="Document" />
        <el-step title="Biometría" icon="Camera" />
        <el-step title="Finalizado" icon="Check" />
      </el-steps>

      <!-- PASO 0: Datos de Inversión -->
      <div v-show="activeStep === 0" class="step-content">
        <h3 class="step-title">Ingresa los datos de tu inversión</h3>
        <el-form label-position="top" @submit.prevent="createApp">
          <el-form-item label="Producto de inversión">
            <el-select v-model="form.investment_type_id" style="width:100%" @change="onTypeChange">
              <el-option v-for="t in types" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
          </el-form-item>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="Monto a invertir (USD)">
                <el-input-number v-model="form.amount" :min="selectedType?.min_amount || 100" style="width:100%" size="large" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Plazo (días)">
                <el-input-number v-model="form.term_days" :min="selectedType?.min_term_days || 30" :max="selectedType?.max_term_days || 360" style="width:100%" size="large" />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- Resumen rápido si hay selección -->
          <div v-if="selectedType" class="quick-summary">
            <span>Tasa referencial: <strong>{{ selectedType.annual_rate }}%</strong></span>
            <span>Retorno anual aprox: <strong>${{ ((form.amount * selectedType.annual_rate) / 100).toLocaleString('es-EC',{minimumFractionDigits:2}) }}</strong></span>
          </div>

          <div class="step-actions">
            <el-button type="primary" size="large" :loading="loading" @click="createApp">
              Continuar <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- PASO 1: Subir Documentos -->
      <div v-show="activeStep === 1" class="step-content">
        <h3 class="step-title">Sube tus documentos habilitantes</h3>
        <p class="step-subtitle">Necesitamos que subas una foto clara de tu cédula de identidad y una planilla de servicio básico actualizada.</p>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <div class="upload-box">
              <h4>Cédula de Identidad</h4>
              <p>Anverso y reverso en un solo archivo PDF o Imagen</p>
              <el-upload
                class="upload-area"
                drag
                action=""
                :auto-upload="false"
                :on-change="(file) => handleDocChange(file, 'cedula')"
                :limit="1"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">Arrastra o <em>haz clic para subir</em></div>
              </el-upload>
              <el-tag v-if="docs.cedula" type="success" style="margin-top:10px">Documento seleccionado</el-tag>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="upload-box">
              <h4>Planilla de Servicio Básico</h4>
              <p>Agua, luz o teléfono (máximo 3 meses de antigüedad)</p>
              <el-upload
                class="upload-area"
                drag
                action=""
                :auto-upload="false"
                :on-change="(file) => handleDocChange(file, 'planilla')"
                :limit="1"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">Arrastra o <em>haz clic para subir</em></div>
              </el-upload>
              <el-tag v-if="docs.planilla" type="success" style="margin-top:10px">Documento seleccionado</el-tag>
            </div>
          </el-col>
        </el-row>

        <div class="step-actions">
          <el-button @click="activeStep--">Atrás</el-button>
          <el-button type="primary" :loading="loading" @click="uploadDocuments">
            Subir Documentos e Ir a Biometría <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- PASO 2: Validación Biométrica (Webcam) -->
      <div v-show="activeStep === 2" class="step-content">
        <h3 class="step-title">Validación Biométrica</h3>
        <p class="step-subtitle">Para tu seguridad, necesitamos una foto de tu rostro. Por favor, mira a la cámara y asegúrate de tener buena iluminación.</p>
        
        <div class="camera-container">
          <video v-show="!photo" ref="videoRef" autoplay playsinline class="webcam-video"></video>
          <canvas ref="canvasRef" style="display:none;"></canvas>
          <img v-if="photo" :src="photo" class="webcam-photo" />

          <div class="camera-controls">
            <el-button v-if="!cameraActive && !photo" type="primary" @click="initCamera">Activar Cámara</el-button>
            <el-button v-if="cameraActive && !photo" type="success" :icon="Camera" size="large" @click="takePhoto" circle></el-button>
            <el-button v-if="photo" type="warning" @click="retakePhoto">Tomar de nuevo</el-button>
          </div>
        </div>

        <div class="step-actions">
           <el-button type="primary" size="large" :loading="loading" :disabled="!photo" @click="submitBiometric">
            Validar Identidad y Finalizar <el-icon class="el-icon--right"><Check /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- PASO 3: Éxito -->
      <div v-show="activeStep === 3" class="step-content success-step">
        <el-result
          icon="success"
          title="¡Solicitud Enviada!"
          sub-title="Tu solicitud de ingreso de Depósito a Plazo Fijo ha sido recibida y está en proceso de revisión por uno de nuestros analistas. Serás notificado por correo sobre el progreso."
        >
          <template #extra>
            <el-button type="primary" @click="$router.push('/client')">Volver al inicio</el-button>
          </template>
        </el-result>
      </div>

    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { investmentApi } from '@/api'
import { useToast } from 'vue-toastification'
import { ArrowRight, UploadFilled, Camera, Check } from '@element-plus/icons-vue'
import type { InvestmentType } from '@/types'

const toast = useToast()
const activeStep = ref(0)
const loading = ref(false)

// Step 1
const types = ref<InvestmentType[]>([])
const form = reactive({ investment_type_id: null as number | null, amount: 5000, term_days: 180 })
const selectedType = computed(() => types.value.find(t => t.id === form.investment_type_id))
const createdAppId = ref<number | null>(null)

// Step 2
const docs = reactive({ cedula: null as File | null, planilla: null as File | null })

// Step 3 (Camera)
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const cameraStream = ref<MediaStream | null>(null)
const cameraActive = ref(false)
const photo = ref<string | null>(null)
const photoBlob = ref<Blob | null>(null)


onMounted(async () => {
  try {
    const { data } = await investmentApi.listTypes()
    types.value = data.filter((t: InvestmentType) => t.is_active)
    if (types.value.length > 0) form.investment_type_id = types.value[0].id
  } catch { toast.error('Error al cargar tipos de inversión') }
})

onUnmounted(() => { stopCamera() })

function onTypeChange() {
  if (!selectedType.value) return
  if (form.amount < (selectedType.value.min_amount || 0)) form.amount = selectedType.value.min_amount || 0
  if (form.term_days < selectedType.value.min_term_days) form.term_days = selectedType.value.min_term_days
  if (form.term_days > selectedType.value.max_term_days) form.term_days = selectedType.value.max_term_days
}

async function createApp() {
  if (!form.investment_type_id) return toast.warning('Selecciona un producto')
  loading.value = true
  try {
    const { data } = await investmentApi.createApplication(form)
    createdAppId.value = data.id
    activeStep.value = 1
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Error al crear solicitud')
  } finally { loading.value = false }
}

function handleDocChange(file: any, type: 'cedula'|'planilla') {
  docs[type] = file.raw
}

async function uploadDocuments() {
  if (!docs.cedula || !docs.planilla) return toast.warning('Sube la cédula y la planilla')
  if (!createdAppId.value) return
  
  loading.value = true
  try {
    await investmentApi.uploadDocument(createdAppId.value, 'cedula', docs.cedula)
    await investmentApi.uploadDocument(createdAppId.value, 'planilla_servicio_basico', docs.planilla)
    activeStep.value = 2
    initCamera()
  } catch { toast.error('Error al subir los documentos') }
  finally { loading.value = false }
}

// === Cámara ===
async function initCamera() {
  try {
    cameraStream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
    if (videoRef.value) {
      videoRef.value.srcObject = cameraStream.value
      cameraActive.value = true
    }
  } catch (err) {
    toast.error('No se pudo acceder a la cámara. Revisa los permisos del navegador.')
  }
}

function stopCamera() {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach(track => track.stop())
    cameraStream.value = null
    cameraActive.value = false
  }
}

function takePhoto() {
  if (!videoRef.value || !canvasRef.value) return
  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d')?.drawImage(video, 0, 0)
  
  photo.value = canvas.toDataURL('image/jpeg', 0.8)
  canvas.toBlob((blob) => { photoBlob.value = blob }, 'image/jpeg', 0.8)
  stopCamera()
}

function retakePhoto() {
  photo.value = null
  photoBlob.value = null
  initCamera()
}

async function submitBiometric() {
  if (!photoBlob.value) return toast.warning('Toma una foto primero')
  if (!createdAppId.value) return
  
  loading.value = true
  try {
    await investmentApi.uploadBiometric(createdAppId.value, photoBlob.value)
    toast.success('Validación biométrica exitosa')
    activeStep.value = 3
  } catch { toast.error('Error en la validación de identidad') }
  finally { loading.value = false }
}

</script>

<style scoped>
.apply-container { max-width: 900px; margin: 0 auto; }
.stepper-card { padding: 20px 40px; border-radius: 12px; }

.step-content { animation: fadeIn 0.4s ease; padding: 20px 0; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(15px); } to { opacity: 1; transform: translateX(0); } }

.step-title { font-size: 1.4rem; color: #1a3c5e; margin-bottom: 8px; text-align: center; }
.step-subtitle { color: #64748b; text-align: center; margin-bottom: 30px; font-size: 0.95rem; }

.quick-summary { background: #f0f4f8; padding: 12px 20px; border-radius: 8px; display: flex; justify-content: space-between; margin-bottom: 24px; color: #1a3c5e; }

.step-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 32px; border-top: 1px solid #e2e8f0; padding-top: 20px; }

/* Document Uploads */
.upload-box { background: #fafafa; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; height: 100%; }
.upload-box h4 { margin-top: 0; color: #1e293b; }
.upload-box p { font-size: 0.8rem; color: #64748b; margin-bottom: 16px; }
.upload-area { width: 100%; }

/* Biometrics Camera */
.camera-container { width: 480px; max-width: 100%; margin: 0 auto; background: #0f172a; border-radius: 16px; overflow: hidden; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.2); aspect-ratio: 4/3; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.webcam-video, .webcam-photo { width: 100%; height: 100%; object-fit: cover; }
.camera-controls { position: absolute; bottom: 24px; left: 0; right: 0; display: flex; justify-content: center; z-index: 10; }

.success-step { text-align: center; padding: 40px 0; }
</style>
