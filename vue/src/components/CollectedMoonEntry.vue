<script setup>
  import { computed } from 'vue';
  import { useStore } from '../store';
  import { areMoonsEqual, moonToString } from '../composables';

  const props = defineProps({
    moon: Object,
  });

  const store = useStore();

  const isMoonUnmentioned = computed(() => {
    return (
      !props.moon.is_story &&
      !store.mentionedMoons.some((possibleMoons) =>
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
    <span class="tooltip material-symbols-outlined"
      >error<span class="tooltiptext">Not mentioned by Talkatoo</span></span
    >
  </div>
  <span v-else @click="store.setMoonUncollected(moon)">{{ moonString }}</span>
</template>
