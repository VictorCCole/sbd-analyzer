<template>
    <div>
      <label class="font-semibold">Movimento:</label>
      <select v-model="movimentoSelecionado" class="border rounded px-3 py-1 mt-1 w-full">
        <option value="squat">Agachamento</option>
        <option value="bench">Supino</option>
        <option value="deadlift">Levantamento Terra</option>
      </select>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    computed: {
      movimentoSelecionado: {
        get() {
          return this.modelValue;
        },
        set(valor) {
          this.$emit('update:modelValue', valor);
        }
      }
    }
  };
  </script>