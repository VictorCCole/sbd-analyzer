<template>
    <div>
      <label class="font-semibold">Vídeo:</label>
      <input type="file" accept="video/*" @change="onFileChange" class="mt-1" />
      <video v-if="videoUrl" :src="videoUrl" controls class="mt-3 max-w-full" />
    </div>
  </template>
  
  <script lang="ts">
  export default {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    data() {
      return {
        videoUrl: ''
      };
    },
    methods: {
      onFileChange(event: Event) {
        const file = (event.target as HTMLInputElement).files?.[0];
        if (file) {
          this.$emit('update:modelValue', file);
          this.videoUrl = URL.createObjectURL(file);
        }
      }
    }
  };
  </script>