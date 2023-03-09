<script setup>
  import { computed } from 'vue';
  import { useState } from '../../stores/state';
  import { moonToString } from '../../composables';
  import MoonEntry from './MoonEntry.vue';

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
  <MoonEntry :moon="moon">
    <div class="list-item-content">
      <span v-html="moonToString(moon)"></span>
    </div>
    <template v-slot:tooltip>
      <v-tooltip :text="tooltipText" location="bottom">
        <template v-slot:activator="{ props }">
          <v-icon v-bind="props" class="ml-auto" icon="mdi-alert-circle-outline" size="20"></v-icon>
        </template>
      </v-tooltip>
    </template>
  </MoonEntry>
</template>
