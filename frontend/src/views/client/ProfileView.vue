<template>
  <div class="profile-container">
    <div class="page-header">
      <h2>👤 Mi Perfil</h2>
      <p>Administra tu información personal y verifica tu identidad biométrica.</p>
    </div>

    <!-- Bandera de estado KYC -->
    <el-alert
      v-if="!authStore.user?.is_kyc_verified"
      title="⚠️ Identidad no verificada"
      type="warning"
      description="Para poder aplicar a inversiones y operaciones de alto valor, debes completar la verificación de identidad biométrica. Sigue los pasos a continuación."
      show-icon
      :closable="false"
      style="margin-bottom: 24px;"
    />
    <el-alert
      v-else
      title="✅ Identidad verificada con IA"
      type="success"
      description="Tu rostro ha sido enrolado correctamente en el sistema. Puedes operar de forma segura."
      show-icon
      :closable="false"
      style="margin-bottom: 24px;"
    />

    <el-row :gutter="24">
      <!-- Datos del usuario -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span style="font-weight:600">Información Personal</span>
          </template>
          <div class="user-info-item">
            <span>Nombre</span><strong>{{ authStore.user?.name }}</strong>
          </div>
          <div class="user-info-item">
            <span>Email</span><strong>{{ authStore.user?.email }}</strong>
          </div>
          <div class="user-info-item">
            <span>Rol</span>
            <el-tag size="small" type="primary">{{ authStore.user?.role }}</el-tag>
          </div>
          <div class="user-info-item">
            <span>Estado KYC</span>
            <el-tag size="small" :type="authStore.user?.is_kyc_verified ? 'success' : 'danger'">
              {{ authStore.user?.is_kyc_verified ? 'Verificado 🤖' : 'Pendiente' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <!-- Asistente de Enrolamiento Biométrico -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span style="font-weight:600">🧠 Verificación de Identidad (KYC Biométrico)</span>
          </template>

          <div v-if="authStore.user?.is_kyc_verified" class="already-verified">
            <el-result icon="success" title="¡Ya estás verificado!" sub-title="Tu identidad fue validada mediante Inteligencia Artificial comparando tu cédula y tu rostro en tiempo real.">
              <template #extra>
                <el-button type="primary" @click="resetKyc">Re-enrollar mi rostro</el-button>
              </template>
            </el-result>
          </div>

          <div v-else>
            <el-steps :active="kycStep" finish-status="success" simple style="margin-bottom: 28px;">
              <el-step title="Foto Cédula" icon="IdCard" />
              <el-step title="Selfie en vivo" icon="Camera" />
              <el-step title="Verificando IA" icon="Cpu" />
            </el-steps>

            <!-- KYC PASO 0: Subir foto de la cédula -->
            <div v-show="kycStep === 0">
              <div class="instruction-box">
                <h4>📋 Paso 1: Foto de tu Cédula</h4>
                <ul class="instructions-list">
                  <li>🔲 Ubica tu cédula sobre una <strong>superficie plana y clara</strong></li>
                  <li>💡 Asegúrate de que <strong>no haya reflejos ni sombras</strong> sobre la foto</li>
                  <li>👁️ El <strong>rostro de la foto de la cédula debe verse claramente</strong></li>
                  <li>📐 La imagen debe estar <strong>bien enfocada y sin cortes</strong></li>
                </ul>
              </div>

              <div class="upload-zone" :class="{ 'has-file': idCardFile }">
                <el-upload
                  class="id-uploader"
                  action=""
                  :auto-upload="false"
                  accept="image/*"
                  :on-change="handleIdCardChange"
                  :show-file-list="false"
                  drag
                >
                  <div v-if="idCardPreview" class="preview-wrapper">
                    <img :src="idCardPreview" class="id-preview" />
                  </div>
                  <div v-else>
                    <el-icon class="el-icon--upload" :size="52" color="#2575bc"><UploadFilled /></el-icon>
                    <div class="upload-text">Arrastra o <em>haz clic para subir</em> la foto de tu cédula</div>
                    <div class="upload-hint">JPG, PNG — Resolución mínima recomendada: 640×480</div>
                  </div>
                </el-upload>
              </div>

              <div class="step-actions">
                <el-button
                  type="primary"
                  size="large"
                  :disabled="!idCardFile"
                  @click="kycStep = 1; initKycCamera()"
                >
                  Continuar con Selfie <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- KYC PASO 1: Selfie en vivo por webcam -->
            <div v-show="kycStep === 1">
              <div class="instruction-box">
                <h4>🤳 Paso 2: Toma tu Selfie</h4>
                <ul class="instructions-list">
                  <li>💡 Busca un lugar con <strong>buena iluminación frontal (de frente)</strong></li>
                  <li>🚫 <strong>No uses gafas de sol</strong> ni objetos que cubran tu rostro</li>
                  <li>👀 Mira <strong>directamente hacia la cámara</strong></li>
                  <li>😐 Mantén una <strong>expresión natural y relajada</strong></li>
                </ul>
              </div>

              <div class="camera-container">
                <video v-show="!kycPhoto" ref="kycVideoRef" autoplay playsinline class="webcam-video"></video>
                <canvas ref="kycCanvasRef" style="display:none;"></canvas>
                <img v-if="kycPhoto" :src="kycPhoto" class="webcam-photo" />

                <!-- Overlay guia de encuadre facial -->
                <div v-if="kycCameraActive && !kycPhoto" class="face-guide">
                  <div class="face-oval"></div>
                </div>

                <div class="camera-controls">
                  <el-button v-if="!kycCameraActive && !kycPhoto" type="primary" size="large" @click="initKycCamera">
                    <el-icon><Camera /></el-icon> Activar Cámara
                  </el-button>
                  <el-button v-if="kycCameraActive && !kycPhoto" type="success" size="large" circle :icon="Camera" @click="takeKycPhoto" />
                  <el-button v-if="kycPhoto" type="warning" @click="retakeKycPhoto">Tomar de nuevo</el-button>
                </div>
              </div>

              <div class="step-actions">
                <el-button @click="kycStep = 0; stopKycCamera()">Atrás</el-button>
                <el-button
                  type="primary"
                  size="large"
                  :loading="enrolling"
                  :disabled="!kycPhoto"
                  @click="submitEnrollment"
                >
                  <el-icon v-if="!enrolling"><Check /></el-icon>
                  {{ enrolling ? 'Procesando con IA...' : 'Verificar mi Identidad' }}
                </el-button>
              </div>
            </div>

            <!-- KYC PASO 2: Procesando -->
            <div v-show="kycStep === 2" class="processing-step">
              <el-icon class="ai-spinner" :size="72" color="#2575bc"><Loading /></el-icon>
              <h3>Analizando con Inteligencia Artificial...</h3>
              <p>Comparando tu rostro con los datos de tu cédula. Por favor espera, esto puede tomar unos segundos.</p>
            </div>

          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { ArrowRight, UploadFilled, Camera, Check, Loading } from '@element-plus/icons-vue'
import { kycApi } from '@/api'

const authStore = useAuthStore()
const toast = useToast()

const kycStep = ref(0)
const enrolling = ref(false)

// ID Card
const idCardFile = ref<File | null>(null)
const idCardPreview = ref<string | null>(null)

// Camera
const kycVideoRef = ref<HTMLVideoElement | null>(null)
const kycCanvasRef = ref<HTMLCanvasElement | null>(null)
const kycCameraStream = ref<MediaStream | null>(null)
const kycCameraActive = ref(false)
const kycPhoto = ref<string | null>(null)
const kycPhotoBlob = ref<Blob | null>(null)

onUnmounted(() => { stopKycCamera() })

function resetKyc() {
  kycStep.value = 0
  idCardFile.value = null
  idCardPreview.value = null
  kycPhoto.value = null
  kycPhotoBlob.value = null
}

function handleIdCardChange(file: any) {
  idCardFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => { idCardPreview.value = e.target?.result as string }
  reader.readAsDataURL(file.raw)
}

async function initKycCamera() {
  try {
    kycCameraStream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 640, height: 480 } })
    if (kycVideoRef.value) {
      kycVideoRef.value.srcObject = kycCameraStream.value
      kycCameraActive.value = true
    }
  } catch {
    toast.error('No se pudo acceder a la cámara. Revisa los permisos del navegador.')
  }
}

function stopKycCamera() {
  if (kycCameraStream.value) {
    kycCameraStream.value.getTracks().forEach(t => t.stop())
    kycCameraStream.value = null
    kycCameraActive.value = false
  }
}

function takeKycPhoto() {
  if (!kycVideoRef.value || !kycCanvasRef.value) return
  const video = kycVideoRef.value
  const canvas = kycCanvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d')?.drawImage(video, 0, 0)
  kycPhoto.value = canvas.toDataURL('image/jpeg', 0.9)
  canvas.toBlob((blob) => { kycPhotoBlob.value = blob }, 'image/jpeg', 0.9)
  stopKycCamera()
}

function retakeKycPhoto() {
  kycPhoto.value = null
  kycPhotoBlob.value = null
  initKycCamera()
}

async function submitEnrollment() {
  if (!idCardFile.value || !kycPhotoBlob.value) {
    toast.warning('Completa ambos pasos antes de continuar.')
    return
  }
  enrolling.value = true
  kycStep.value = 2

  try {
    const formData = new FormData()
    formData.append('id_card', idCardFile.value, 'cedula.jpg')
    formData.append('selfie', kycPhotoBlob.value, 'selfie.jpg')

    const { data } = await kycApi.enroll(idCardFile.value, kycPhotoBlob.value)

    if (data.verified) {
      toast.success('✅ Identidad verificada exitosamente con IA.')
      // Actualizar el usuario en el store
      await authStore.refreshUser()
      kycStep.value = 0
    } else {
      toast.error(`❌ ${data.message || 'Los rostros no coinciden. Intenta de nuevo.'}`)
      kycStep.value = 1
      retakeKycPhoto()
    }
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Error durante la validación biométrica.')
    kycStep.value = 1
    retakeKycPhoto()
  } finally {
    enrolling.value = false
  }
}
</script>

<style scoped>
.profile-container { max-width: 1100px; margin: 0 auto; }

.user-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9rem;
}
.user-info-item:last-child { border-bottom: none; }
.user-info-item span { color: #64748b; }

.instruction-box {
  background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 20px;
}
.instruction-box h4 { margin: 0 0 10px; color: #1e40af; font-size: 1rem; }
.instructions-list { margin: 0; padding-left: 0; list-style: none; color: #374151; }
.instructions-list li { padding: 4px 0; font-size: 0.875rem; line-height: 1.5; }

.upload-zone { margin-bottom: 20px; }
.id-uploader { width: 100%; }
.preview-wrapper { padding: 10px; }
.id-preview { max-width: 100%; max-height: 200px; border-radius: 8px; object-fit: contain; }
.upload-text { font-size: 0.95rem; color: #374151; margin-top: 10px; }
.upload-hint { font-size: 0.8rem; color: #9ca3af; margin-top: 4px; }

.camera-container {
  width: 480px;
  max-width: 100%;
  margin: 0 auto 20px;
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  aspect-ratio: 4/3;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.webcam-video, .webcam-photo { width: 100%; height: 100%; object-fit: cover; }
.camera-controls {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 10;
}

/* Guia facial */
.face-guide {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.face-oval {
  width: 160px;
  height: 210px;
  border: 3px solid rgba(56,189,248,0.8);
  border-radius: 50%;
  box-shadow: 0 0 0 2000px rgba(0,0,0,0.25);
  animation: pulse-oval 2s ease-in-out infinite;
}
@keyframes pulse-oval {
  0%, 100% { box-shadow: 0 0 0 2000px rgba(0,0,0,0.25), 0 0 0 0 rgba(56,189,248,0.4); }
  50% { box-shadow: 0 0 0 2000px rgba(0,0,0,0.25), 0 0 0 8px rgba(56,189,248,0); }
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.processing-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #1e293b;
}
.processing-step h3 { margin: 20px 0 10px; font-size: 1.3rem; color: #1a3c5e; }
.processing-step p { color: #64748b; font-size: 0.95rem; max-width: 400px; }
.ai-spinner { animation: spin 1.2s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.already-verified { padding: 10px 0; }
</style>
