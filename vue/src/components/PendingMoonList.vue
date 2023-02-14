<script setup>
  import { computed } from 'vue';
  import { storeToRefs } from 'pinia';
  import { useStore } from '../store';

  const props = defineProps({
    moons: Array,
  });

  const store = useStore();

  const filteredMoons = computed(() => {
    const correctMoons = store.selectedKingdomPendingMoons
      .map((possibleMoons) => possibleMoons.find((moon) => moon.correct))
      .filter((moon) => moon);
    const collectedOrCorrectMoons = [...store.collectedMoons, correctMoons];

    return moons
      .map((possibleMoons) =>
        possibleMoons.filter(
          (moon) =>
            !collectedOrCorrectMoons.value.some(
              (m) => m.index !== moon.index && moonsAreEqual(moon, m)
            )
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
