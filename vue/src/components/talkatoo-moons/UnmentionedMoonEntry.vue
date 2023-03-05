<script setup>
  import { computed } from 'vue';
  import { useState } from '../../stores/state';
  import { moonToString } from '../../composables';

  const props = defineProps({
    moon: Object,
  });

  const state = useState();

  const tooltipText = computed(() => {
    return props.moon.is_story
      ? "Story moons don't count in Hardcore"
      : 'Not mentioned by Talkatoo';
  });
</script>

<template>
  <div class="list-item-content">
    <span v-html="moonToString(moon)"></span>
    <span class="tooltip ml-4">
      <v-icon icon="mdi-alert-circle-outline" size="24"></v-icon>
      <span class="tooltip-text">{{ tooltipText }}</span>
    </span>
  </div>
</template>
