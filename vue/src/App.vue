<script setup>
  import TalkatooMoons from '@/components/talkatoo-moons/TalkatooMoons.vue';
  import MoonList from '@/components/moon-list/MoonList.vue';
  import Settings from '@/components/settings/Settings.vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { useDisplay } from 'vuetify';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { isMoonCollected, scrollToTop } from '@/composables';
  import { areMoonsEqual } from './composables';

  const state = useState();
  const settings = useSettings();
  const { lgAndUp } = useDisplay();
  const { globalProperties } = useCurrentInstance();

  function getMoonsByKingdom() {
    globalProperties.$eel
      .get_moons_by_kingdom()()
      .then((response) => {
        state.setMoonsByKingdom(response);
      })
      .catch(() => state.showError('Error fetching moon list.'));
  }

  function getSettingsFromFile() {
    globalProperties.$eel.get_settings()((settingsFromFile) => {
      if (settingsFromFile) {
        settings.setSettings(settingsFromFile);
      }
      state.updateKingdoms();
      state.setSelectedKingdom(state.displayedKingdoms[0]);
      if (!settingsFromFile) {
        state.setShowSettings(true);
      }
    });
  }

  function resetRun() {
    globalProperties.$eel
      .reset_run()()
      .then(() => {
        state.resetRun();
      })
      .catch(() => state.showError('Error resetting the run.'));
  }

  function eelAddMentionedMoon(possibleMoons) {
    if (!possibleMoons || possibleMoons.length === 0) return;

    const mostRecentMention = state.mentionedMoons[state.mentionedMoons.length - 1];
    const isEqualToMostRecent =
      possibleMoons.length === mostRecentMention?.length &&
      possibleMoons.every((moon, index) => areMoonsEqual(moon, mostRecentMention[index]));

    if (isEqualToMostRecent) return;

    state.addMentionedMoon(possibleMoons);
    selectKingdom(possibleMoons[0].kingdom);
    state.setShowSettings(false);

    setTimeout(scrollToTop, 50);
  }

  function eelAddCollectedMoon(possibleMoons) {
    if (!possibleMoons || possibleMoons.length !== 1) return;

    const collectedMoon = possibleMoons[0];

    if (isMoonCollected(collectedMoon)) return;

    state.addCollectedMoon(collectedMoon);
    selectKingdom(collectedMoon.kingdom);
    state.setShowSettings(false);
  }

  function eelSetCurrentKingdom(currentKingdom) {
    if (!currentKingdom || currentKingdom === state.currentKingdomName) return;

    state.setCurrentKingdomName(currentKingdom);
    selectKingdom(currentKingdom);
  }

  function selectKingdom(kingdomName) {
    const selectedKingdom = state.displayedKingdoms.find((kingdom) => kingdom.name === kingdomName);

    if (selectedKingdom) {
      state.setSelectedKingdom(selectedKingdom);
    }
  }

  function toggleShowSettings() {
    state.setShowSettings(!state.showSettings);
  }

  globalProperties.$eel.expose(eelAddMentionedMoon, 'add_mentioned_moon');
  globalProperties.$eel.expose(eelAddCollectedMoon, 'add_collected_moon');
  globalProperties.$eel.expose(eelSetCurrentKingdom, 'set_current_kingdom');

  getSettingsFromFile();
  getMoonsByKingdom();
</script>

<template>
  <v-app>
    <v-app-bar flat density="compact">
      <v-tabs v-model="state.selectedKingdom" grow show-arrows color="primary">
        <v-tab
          v-for="kingdom in state.displayedKingdoms"
          :key="kingdom.name"
          :value="kingdom"
          class="clickable">
          {{ kingdom.name }}
        </v-tab>
      </v-tabs>
      <v-icon @click="resetRun" icon="mdi-history" size="30" class="ml-4 clickable"></v-icon>
      <v-icon
        @click="toggleShowSettings"
        :icon="state.showSettings ? 'mdi-home' : 'mdi-cog'"
        size="30"
        class="mx-4 clickable"></v-icon>
    </v-app-bar>
    <v-main>
      <v-container
        fluid
        class="image-container pa-8"
        :style="{ backgroundImage: `url(${state.selectedKingdom.image})` }">
        <Settings
          v-if="state.showSettings"
          class="main-content scrollable scroll-container mx-auto" />
        <div v-else-if="lgAndUp" class="d-flex align-start">
          <TalkatooMoons class="main-content scrollable scroll-container mx-auto" />
          <MoonList class="scrollable ml-8 main-content-height" />
        </div>
        <div v-else class="main-content-column">
          <TalkatooMoons class="scrollable scroll-container flex-grow min-height" />
          <MoonList class="scrollable mt-8 flex-shrink min-height" />
        </div>
      </v-container>
    </v-main>
    <v-snackbar v-model="state.snackbar.visible" :color="state.snackbar.color" timeout="2000">
      {{ state.snackbar.text }}
      <template v-slot:actions>
        <v-icon
          @click="() => state.closeSnackbar()"
          icon="mdi-close"
          size="small"
          class="clickable"></v-icon>
      </template>
    </v-snackbar>
  </v-app>
</template>
