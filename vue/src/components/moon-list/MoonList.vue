<script setup>
  import PendingMoonList from './PendingMoonList.vue';
  import CollectedMoonList from './CollectedMoonList.vue';

  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { areMoonsPending } from '@/composables';

  const state = useState();

  const selectedKingdomPendingMoons = computed(() => {
    return state.mentionedMoons.filter(areMoonsPending);
  });

  const selectedKingdomCollectedMoons = computed(() => {
    return state.collectedMoons.filter((moon) => moon.kingdom === state.selectedKingdom);
  });
</script>

<template>
  <v-card
    v-if="selectedKingdomPendingMoons.length > 0 || selectedKingdomCollectedMoons.length > 0"
    flat
    rounded="lg"
    style="opacity: 0.95">
    <v-card-text>
      <div class="list-container">
        <PendingMoonList
          v-if="selectedKingdomPendingMoons.length > 0"
          :moons="selectedKingdomPendingMoons" />
        <CollectedMoonList
          v-if="selectedKingdomCollectedMoons.length > 0"
          :moons="selectedKingdomCollectedMoons" />
      </div>
    </v-card-text>
  </v-card>
</template>
