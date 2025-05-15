<!-- src/views/HomeView.vue -->
<template>
  <UploadVideo @feedback-recebido="feedback = $event" />
  <Feedback :feedback="feedback" />
</template>

<script setup lang="ts">
import UploadVideo from '@/components/UploadVideo.vue'
import Feedback from '@/components/Feedback.vue'
import { ref } from 'vue'

const feedback = ref<string[]>([])
</script>
