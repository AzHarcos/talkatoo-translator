<script setup>
  import { computed } from 'vue';
  import { useState } from '../../stores/state';
  import { areMoonsEqual, moonToString } from '../../composables';

  const props = defineProps({
    moon: Object,
  });

  const state = useState();

  const isMoonUnmentioned = computed(() => {
    return (
      !props.moon.is_story &&
      !state.mentionedMoons.some((possibleMoons) =>
        possibleMoons.some((m) => areMoonsEqual(props.moon, m))
      )
    );
  });

  const moonString = computed(() => {
    return moonToString(props.moon);
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
