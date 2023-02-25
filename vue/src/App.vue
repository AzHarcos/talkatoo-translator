<script setup>
  import MoonList from '@/components/moon-list/MoonList.vue';
  import Settings from '@/components/settings/Settings.vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';

  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { isMoonCollected, scrollToTop } from '@/composables';

  const state = useState();
  const settings = useSettings();
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
      settings.setSettings(settingsFromFile);
      state.setShowSettings(true);
    });
  }

  function updateMoons() {
    globalProperties.$eel.get_mentioned_moons()((response) => {
      if (response.length > state.mentionedMoons.length) {
        const newlyMentionedMoons = response.slice(state.mentionedMoons.length - response.length);

        newlyMentionedMoons.forEach((possibleMoons) => {
          const moonsWithIndex = possibleMoons.map((moon) => ({
            ...moon,
            index: state.mentionedMoons.length,
            correct: possibleMoons.length === 0,
          }));
          state.addMentionedMoons(moonsWithIndex);
        });

        const latestMoon = response[response.length - 1][0];
        selectKingdom(latestMoon.kingdom);
        state.setShowSettings(false);

        setTimeout(scrollToTop, 10);
      }
    });
    globalProperties.$eel.get_collected_moons()((response) => {
      const definiteCollectedMoons = response
        .filter((possibleMoons) => possibleMoons.length === 1)
        .map((possibleMoons) => possibleMoons[0]);
      const newlyCollectedMoons = definiteCollectedMoons.filter((moon) => !isMoonCollected(moon));

      if (newlyCollectedMoons.length === 0) return;

      const latestMoon = newlyCollectedMoons[newlyCollectedMoons.length - 1];
      selectKingdom(latestMoon.kingdom);
      state.setShowSettings(false);

      state.addCollectedMoons(newlyCollectedMoons);
    });
  }

  function selectKingdom(kingdom) {
    state.setSelectedKingdom(kingdom);
  }

  function toggleShowSettings() {
    state.setShowSettings(!state.showSettings);
  }

  const backgroundImageStyle = computed(() => {
    const imageUrl = `http://localhost:8083/assets/${state.selectedKingdom}.png`;
    return {
      backgroundImage: `url(${imageUrl})`,
    };
  });

  getSettingsFromFile();
  getMoonsByKingdom();
  setInterval(updateMoons, 1000);
</script>

<template>
  <v-app>
    <v-app-bar flat density="compact">
      <v-tabs v-model="state.selectedKingdom" grow show-arrows color="primary">
        <v-tab
          v-for="kingdom in settings.activeKingdoms"
          :key="kingdom"
          :value="kingdom"
          class="clickable">
          {{ kingdom }}
        </v-tab>
      </v-tabs>
      <v-icon
        @click="toggleShowSettings"
        :icon="state.showSettings ? 'mdi-home' : 'mdi-cog'"
        size="30"
        class="mx-4 clickable"></v-icon>
    </v-app-bar>
    <v-main>
      <v-container fluid class="image-container pa-8" :style="backgroundImageStyle">
        <div class="main-content"><Settings v-if="state.showSettings" /> <MoonList v-else /></div>
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
