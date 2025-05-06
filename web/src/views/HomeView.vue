<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">
    <h1 class="text-2xl font-bold mb-6">Análise de Levantamentos</h1>

    <!-- Seletor de movimento -->
    <SelectMovimento v-model="movimento" class="mb-4 w-full max-w-sm" />

    <!-- Upload de vídeo -->
    <UploadVideo v-model="video" class="mb-4 w-full max-w-sm" />

    <!-- Botão de envio -->
    <button
      :disabled="!video || !movimento"
      @click="enviarVideo"
      class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded disabled:opacity-50"
    >
      Enviar para Análise
    </button>

    <!-- Feedback -->
    <Feedback :feedback="feedback" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import SelectMovimento from '@/components/SelectMovimento.vue';
import UploadVideo from '@/components/UploadVideo.vue';
import Feedback from '@/components/Feedback.vue';

export default defineComponent({
  components: {
    SelectMovimento,
    UploadVideo,
    Feedback
  },
  setup() {
    const movimento = ref('squat');
    const video = ref<File | null>(null);
    const feedback = ref('');

    const enviarVideo = async () => {
      if (!video.value || !movimento.value) return;

      const formData = new FormData();
      formData.append('movimento', movimento.value);
      formData.append('video', video.value);

      try {
        const response = await fetch('/api/analisar', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        feedback.value = data.feedback || 'Nenhum feedback retornado.';
      } catch (error) {
        feedback.value = 'Erro ao enviar o vídeo para análise.';
      }
    };

    return {
      movimento,
      video,
      feedback,
      enviarVideo
    };
  }
});
</script>

<style scoped>
button {
  transition: all 0.2s;
}
</style>