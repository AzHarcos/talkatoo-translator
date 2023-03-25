<script setup>
  import TalkatooMoons from '@/components/talkatoo-moons/TalkatooMoons.vue';
  import MoonList from '@/components/moon-list/MoonList.vue';
  import Settings from '@/components/settings/Settings.vue';
  import ResetConfirmationDialog from '@/components/dialogs/ResetConfirmationDialog.vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { ref } from 'vue';
  import { useDisplay } from 'vuetify';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { isMoonMentioned, isMoonCollected, scrollToTop, areMoonsEqual } from '@/composables';

  const state = useState();
  const settings = useSettings();
  const showResetConfirmationDialog = ref(false);
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

  function resetRun(skipResetConfirmation) {
    globalProperties.$eel
      .reset_run(skipResetConfirmation)()
      .then(() => {
        closeResetConfirmationDialog();
        state.resetRun();
        if (skipResetConfirmation) {
          settings.setSkipResetConfirmation(skipResetConfirmation);
        }
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

    const filteredOptions = possibleMoons.filter(
      (moon) => !isMoonMentioned(moon) && !isMoonCollected(moon)
    );

    if (filteredOptions.length === 0) return;

    state.addMentionedMoon(filteredOptions);
    selectKingdom(filteredOptions[0].kingdom);
    state.setShowSettings(false);

    setTimeout(scrollToTop, 50);
  }

  function eelAddCollectedMoon(possibleMoons) {
    if (!possibleMoons || possibleMoons.length !== 1) return;

    const collectedMoon = possibleMoons[0];

    if (isMoonCollected(collectedMoon)) return;

    state.addCollectedMoon(collectedMoon);

    if (!collectedMoon.collection_kingdom) {
      selectKingdom(collectedMoon.kingdom);
    } else if (collectedMoon.kingdom !== state.selectedKingdom.name) {
      state.showSuccess(
        `Collected ${collectedMoon.id} - ${collectedMoon[settings.outputLanguage]}`
      );
    }

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

  function openResetConfirmationDialog() {
    if (settings.skipResetConfirmation) {
      resetRun();
    } else {
      showResetConfirmationDialog.value = true;
    }
  }

  function closeResetConfirmationDialog() {
    showResetConfirmationDialog.value = false;
  }

  globalProperties.$eel.expose(eelAddMentionedMoon, 'add_mentioned_moon');
  globalProperties.$eel.expose(eelAddCollectedMoon, 'add_collected_moon');
  globalProperties.$eel.expose(eelSetCurrentKingdom, 'set_current_kingdom');

  getSettingsFromFile();
  getMoonsByKingdom();

  document.addEventListener('keydown', (event) => {
    if (event.key === 'F5') {
      event.preventDefault();
      openResetConfirmationDialog();
    }
  });
</script>

<template>
  <v-app>
    <ResetConfirmationDialog
      v-if="showResetConfirmationDialog"
      @confirm="resetRun"
      @close="closeResetConfirmationDialog" />
    <v-app-bar flat density="compact">
      <v-tabs v-model="state.selectedKingdom" grow show-arrows color="primary">
        <v-tab
          v-for="kingdom in state.displayedKingdoms"
          :key="kingdom.name"
          :value="kingdom"
          :disabled="state.showSettings"
          class="clickable">
          {{ kingdom.name }}
        </v-tab>
      </v-tabs>
      <v-icon
        @click="openResetConfirmationDialog"
        icon="mdi-history"
        size="30"
        class="ml-4 clickable"></v-icon>
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
