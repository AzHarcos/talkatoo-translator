<script setup>
  const props = defineProps({
    moons: Array,
  });
</script>

<template>
  <div class="list-wrapper">
    <div class="list-header">Collected Moons:</div>
    <ul class="list">
      <li v-for="moon in moons" class="list-item">
        <CollectedMoonEntry :moon="moon" />
      </li>
    </ul>
  </div>
</template>
