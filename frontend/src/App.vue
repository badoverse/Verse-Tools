
<script setup>

import { ref, onMounted } from "vue";
import { getData } from "@/api/msg-api";

const dati = ref([]);

onMounted(async () => {
  dati.value = await getData();
});
</script>

<template>
  <h1>You did it!</h1>
  <p>
    Visit <a href="https://vuejs.org/" target="_blank" rel="noopener">vuejs.org</a> to read the
    documentation
  </p>
  <div v-for="item in dati" :key="item.id">
    {{ item }}
  </div>
</template>

<style scoped></style>
