<script setup>
  import { computed } from 'vue';
  import { useSettings } from '@/stores/settings';
  import { useState } from '@/stores/state';
  import { areMoonsEqual, correctMoonOptional } from '../../composables';

  const state = useState();
  const settings = useSettings();

  const moonList = computed(() => {
    return state.moonsByKingdom[state.selectedKingdom.name];
  });

  function addMoonToMentioned(moon) {
    const moonHasBeenCollected = state.collectedMoons.some((m) => areMoonsEqual(moon, m));

    if (moonHasBeenCollected) {
      state.showError('Moon has already been collected.');
      return;
    }

    const moonHasBeenMentioned = state.mentionedMoons.some((possibleMoons) =>
      areMoonsEqual(moon, correctMoonOptional(possibleMoons))
    );

    if (moonHasBeenMentioned) {
      state.showError('Moon has already been mentioned by Talkatoo.');
      return;
    }

    state.addMentionedMoons([moon]);
  }
</script>

<template>
  <v-card flat class="moon-list">
    <v-card-text>
      <div class="text-center text-h5 mb-4 text-decoration-underline">
        {{ state.selectedKingdom.name }} Moons
      </div>
      <ol class="ml-7">
        <li v-for="moon in moonList" @click="() => addMoonToMentioned(moon)" class="clickable">
          <span class="ml-1">
            {{ moon[settings.outputLanguage] }} - {{ moon[settings.inputLanguage] }}
          </span>
        </li>
      </ol>
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .moon-list {
    min-width: 510px;
  }
</style>
