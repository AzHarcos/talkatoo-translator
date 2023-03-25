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
  <v-card flat :class="{ 'moon-list-width': lgAndUp }">
    <v-card-text class="list-container">
      <div class="text-center text-h5 mb-4 text-decoration-underline">Moon List</div>
      <ol :class="{ 'ml-4': !lgAndUp }">
        <li v-for="moon in moonList" @click="() => addMoonToMentioned(moon)" class="clickable ml-4">
          <span class="ml-1">
            {{ moon[settings.outputLanguage] }} - {{ moon[settings.inputLanguage] }}
          </span>
        </li>
      </ol>
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .moon-list-width {
    min-width: 550px;
  }
</style>
