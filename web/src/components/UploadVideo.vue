<template>
  <form @submit.prevent="enviarFormulario" class="formulario">
    <div class="linha">
      <label>Nome:</label>
      <input type="text" v-model="nome" required />
    </div>

    <div class="linha">
      <label>Email:</label>
      <input type="email" v-model="email" required />
    </div>

    <div class="linha">
      <label>Movimento:</label>
      <select v-model="movimento" required>
        <option disabled value="">Selecione</option>
        <option value="squat">Agachamento</option>
        <option value="bench">Supino</option>
        <option value="deadlift">Levantamento Terra</option>
      </select>
    </div>

    <div class="linha">
      <label>Vídeo (.mp4):</label>
      <input type="file" @change="onFileChange" accept="video/mp4" required />
    </div>

    <button type="submit" :disabled="carregando">Enviar</button>

    <div v-if="carregando" class="status">⏳ Enviando vídeo para análise...</div>
    <div v-if="sucesso && !carregando" class="status sucesso">
      ✅ Envio concluído! Verifique seu e-mail.
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const nome = ref('')
const email = ref('')
const movimento = ref('')
const video = ref<File | null>(null)

const carregando = ref(false)
const sucesso = ref(false)

const emit = defineEmits<{
  (e: 'feedback-recebido', feedback: string[]): void
}>()

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  video.value = target.files?.[0] || null
}

async function enviarFormulario() {
  if (!video.value) return
  carregando.value = true
  sucesso.value = false

  const formData = new FormData()
  formData.append('nome', nome.value)
  formData.append('email', email.value)
  formData.append('movimento', movimento.value)
  formData.append('video', video.value)

  try {
    const response = await fetch('http://localhost:8000/analisar/', {
      method: 'POST',
      body: formData,
    })

    const data = await response.json()
    emit('feedback-recebido', data)
    sucesso.value = true
    alert("✅ Análise enviada com sucesso! Confira seu e-mail e veja o feedback abaixo.")
  } catch (err) {
    alert("❌ Erro ao enviar. Verifique se o back-end está rodando.")
  } finally {
    carregando.value = false
  }
}
</script>

<style scoped>
.formulario {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: #1e1e1e;
  padding: 2rem;
  border-radius: 8px;
  color: #fff;
}

.linha {
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 0.25rem;
  font-weight: bold;
}

input,
select,
button {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: none;
}

input,
select {
  background-color: #2c2c2c;
  color: #fff;
}

button {
  background-color: #4caf50;
  color: white;
  cursor: pointer;
  transition: background 0.3s ease;
}

button:disabled {
  background-color: #888;
  cursor: not-allowed;
}

.status {
  margin-top: 1rem;
  font-size: 0.95rem;
}

.sucesso {
  color: #4caf50;
}
</style>
