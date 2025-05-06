<template>
    <div v-if="feedback" class="p-4 bg-white shadow rounded mt-4">
      <h2 class="font-semibold text-lg mb-2">Feedback:</h2>
      <pre class="text-sm whitespace-pre-wrap">{{ feedback }}</pre>
    </div>
  </template>
  
  <script lang="ts">
  export default {
    props: {
      feedback: String
    }
  };
  </script>