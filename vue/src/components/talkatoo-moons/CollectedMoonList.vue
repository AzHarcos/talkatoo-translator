<script setup>
  import CollectedMoonEntry from './CollectedMoonEntry.vue';
  import UnmentionedMoonEntry from './UnmentionedMoonEntry.vue';

  import { computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { padStart } from '../../composables';

  const props = defineProps({
    moons: Array,
  });

  const state = useState();
  const settings = useSettings();

  function getMoonCount(moons) {
    return moons.reduce((sum, moon) => {
      if (moon.isMentioned === false) return sum;

      if (moon.is_multi) return sum + 3;

      return sum + 1;
    }, 0);
  }

  const collectedMoonCount = computed(() => {
    return getMoonCount(props.moons);
  });

  const requiredMoonCount = computed(() => {
    if (settings.includePostGame && state.moonsByKingdom[state.selectedKingdom.name]) {
      return getMoonCount(state.moonsByKingdom[state.selectedKingdom.name]);
    }

    return state.selectedKingdom.requiredMoonCount;
  });
</script>

<template>
  <div class="list-wrapper">
    <div class="list-header" :class="{ 'mr-1': !requiredMoonCount }">
      <span>Collected Moons:</span>
      <div>
        <span v-html="padStart(collectedMoonCount.toString())"></span>
        <span v-if="requiredMoonCount">/{{ requiredMoonCount }} </span>
      </div>
    </div>
    <ul class="list">
      <li v-for="moon in moons" class="list-item">
        <CollectedMoonEntry v-if="moon.isMentioned" :moon="moon" />
        <UnmentionedMoonEntry v-else :moon="moon" />
      </li>
    </ul>
  </div>
</template>
