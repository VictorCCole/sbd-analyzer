<!-- src/components/Feedback.vue -->
<template>
  <div v-if="feedback.length">
    <h3>Resultado da Análise:</h3>
    <ul>
      <li v-for="(item, index) in feedback" :key="index">{{ item }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
defineProps<{ feedback: string[] }>()
</script>
