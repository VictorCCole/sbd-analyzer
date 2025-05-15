<template>
  <div id="app">
    <header>
      <h1>Sistema de Análise de Powerlifting</h1>
    </header>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
// Não precisa de lógica específica aqui por enquanto
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', sans-serif;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

h1 {
  color: #2c3e50;
}
</style>
