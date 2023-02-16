<script setup>
  import PendingMoonEntry from './PendingMoonEntry.vue';

  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { areMoonsEqual } from '@/composables';

  const props = defineProps({
    moons: Array,
  });

  const state = useState();

  // moons that have been collected or marked as correct
  const definitiveMoons = computed(() => {
    const correctMoons = props.moons
      .map((possibleMoons) => possibleMoons.find((moon) => moon.correct))
      .filter((moon) => moon);

    return [...state.collectedMoons, ...correctMoons];
  });

  const filteredMoons = computed(() => {
    return props.moons
      .map((possibleMoons) =>
        possibleMoons.filter(
          (moon) =>
            !definitiveMoons.value.some((m) => m.index !== moon.index && areMoonsEqual(moon, m))
        )
      )
      .filter((possibleMoons) => possibleMoons.length > 0);
  });
</script>

<template>
  <div class="list-wrapper">
    <div class="list-header">Pending Moons:</div>
    <ul class="list">
      <li v-for="possibleMoons in filteredMoons" class="list-item">
        <PendingMoonEntry :possible-moons="possibleMoons" />
      </li>
    </ul>
  </div>
</template>
