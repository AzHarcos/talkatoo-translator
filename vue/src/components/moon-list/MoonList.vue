<script setup>
  import PendingMoonList from './PendingMoonList.vue';
  import CollectedMoonList from './CollectedMoonList.vue';

  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { areMoonsEqual, areMoonsPending } from '@/composables';

  const state = useState();
  const settings = useSettings();

  const selectedKingdomPendingMoons = computed(() => {
    return state.mentionedMoons.filter(areMoonsPending).reverse();
  });

  const selectedKingdomCollectedMoons = computed(() => {
    const collectedMoons = state.collectedMoons.filter(
      (moon) => moon.kingdom === state.selectedKingdom.name
    );
    return collectedMoons
      .map((moon) => ({
        ...moon,
        isMentioned: isMoonMentioned(moon),
      }))
      .reverse();
  });

  function isMoonMentioned(moon) {
    if (moon.is_story) return !settings.isHardcore;

    return state.mentionedMoons.some((possibleMoons) =>
      possibleMoons.some((m) => areMoonsEqual(moon, m))
    );
  }
</script>

<template>
  <v-card flat>
    <v-card-text>
      <div class="list-container">
        <PendingMoonList
          v-if="state.selectedKingdom.hasTalkatoo"
          :moons="selectedKingdomPendingMoons" />
        <CollectedMoonList :moons="selectedKingdomCollectedMoons" />
      </div>
    </v-card-text>
  </v-card>
</template>
