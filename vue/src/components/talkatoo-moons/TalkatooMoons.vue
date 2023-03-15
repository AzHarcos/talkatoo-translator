<script setup>
  import PendingMoonList from './PendingMoonList.vue';
  import CollectedMoonList from './CollectedMoonList.vue';

  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { isMoonMentioned, isMoonCollected } from '@/composables';

  const state = useState();
  const settings = useSettings();

  const selectedKingdomPendingMoons = computed(() => {
    return state.mentionedMoons.filter(possibleMoons => possibleMoons[0].kingdom === state.selectedKingdom.name && possibleMoons.every((moon) => !isMoonCollected(moon))).reverse();
  });

  const selectedKingdomCollectedMoons = computed(() => {
    const collectedMoons = state.collectedMoons.filter(
      (moon) => moon.kingdom === state.selectedKingdom.name
    );
    return collectedMoons
      .map((moon) => ({
        ...moon,
        isMentioned: showMoonAsMentioned(moon),
      }))
      .reverse();
  });

  function showMoonAsMentioned(moon) {
    if (!state.selectedKingdom.hasTalkatoo) return true;

    if (moon.is_story) return !settings.isHardcore;

    return isMoonMentioned(moon);
  }
</script>

<template>
  <v-card flat>
    <v-card-text>
      <div class="list-container talkatoo-moon-list">
        <div class="text-center text-h5 mb-2 text-decoration-underline">Talkatoo Moons</div>
        <PendingMoonList
          v-if="state.selectedKingdom.hasTalkatoo"
          :moons="selectedKingdomPendingMoons" />
        <CollectedMoonList :moons="selectedKingdomCollectedMoons" />
      </div>
    </v-card-text>
  </v-card>
</template>
