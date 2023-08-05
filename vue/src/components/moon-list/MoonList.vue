<script setup>
  import { computed } from 'vue';
  import { useDisplay } from 'vuetify';

  import { useSettings } from '@/stores/settings';
  import { useState } from '@/stores/state';
  import { isMoonCollected, isMoonMentioned, scrollToTop } from '../../composables';

  const state = useState();
  const settings = useSettings();
  const { lgAndUp } = useDisplay();

  const moonList = computed(() => {
    return state.moonsByKingdom[state.selectedKingdom.name];
  });

  function addMoonToMentioned(moon) {
    if (isMoonCollected(moon)) {
      state.showError('Moon has already been collected.');
      return;
    }

    if (isMoonMentioned(moon)) {
      state.showError('Moon has already been mentioned by Talkatoo.');
      return;
    }

    if (moon.is_story || !state.selectedKingdom.hasTalkatoo) {
      state.addCollectedMoon(moon);
    } else {
      state.addMentionedMoon([moon]);
      setTimeout(scrollToTop, 50);
    }
  }
</script>

<template>
  <v-expansion-panels :class="{ 'moon-list-width': lgAndUp }">
    <v-expansion-panel elevation="0" class="list-container">
      <v-expansion-panel-title>
        <div wix class="text-center text-h5 text-decoration-underline w-100">Moon List</div>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <ol :class="{ 'ml-4': !lgAndUp }">
          <li
            v-for="moon in moonList"
            @click="() => addMoonToMentioned(moon)"
            class="clickable ml-4">
            <span class="ml-1">
              {{ moon[settings.outputLanguage] }} - {{ moon[settings.inputLanguage] }}
            </span>
          </li>
        </ol>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<style scoped>
  .moon-list-width {
    min-width: 550px;
  }
</style>
