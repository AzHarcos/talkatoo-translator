<script setup>
  import { computed } from 'vue';
  import { useState } from '../../stores/state';
  import { useSettings } from '@/stores/settings';
  import { areMoonsEqual, moonToString } from '../../composables';

  const props = defineProps({
    moon: Object,
  });

  const state = useState();
  const settings = useSettings();

  const isMoonUnmentioned = computed(() => {
    if (props.moon.is_story) return settings.isHardcore;

    return !state.mentionedMoons.some((possibleMoons) =>
      possibleMoons.some((m) => areMoonsEqual(props.moon, m))
    );
  });

  const moonString = computed(() => {
    return moonToString(props.moon);
  });

  const tooltipText = computed(() => {
    return settings.isHardcore
      ? "Story moons don't count in Hardcore"
      : 'Not mentioned by Talkatoo';
  });
</script>

<template>
  <div v-if="isMoonUnmentioned" class="list-item-content">
    <span>{{ moonString }}</span>
    <span class="tooltip">
      <v-icon icon="mdi-alert-circle-outline"></v-icon>
      <span class="tooltip-text">Not mentioned by Talkatoo</span>
    </span>
  </div>
  <span v-else @click="state.setMoonUncollected(moon)">{{ moonString }}</span>
</template>
