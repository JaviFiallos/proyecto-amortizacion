<template>
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useInstitutionStore } from '@/stores/institution'

const institutionStore = useInstitutionStore()
onMounted(() => { institutionStore.fetch() })
</script>
