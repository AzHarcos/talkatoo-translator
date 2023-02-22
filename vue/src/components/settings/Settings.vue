<script setup>
  import ImageRecognitionSettings from './ImageRecognitionSettings.vue';
  import KingdomsPicker from './KingdomSettings.vue';
  import LanguageSettings from './LanguageSettings.vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';

  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();

  function closeSettings() {
    state.setShowSettings(false);
  }

  function writeSettingsToFile() {
    const settingsSnapshot = JSON.stringify(settings.$state);
    globalProperties.$eel.write_settings_to_file(settingsSnapshot);
  }
</script>

<template>
  <v-card flat>
    <v-card-title class="ml-1 py-4 d-flex justify-space-between">
      <div class="text-h5">Settings</div>
      <v-icon @click="closeSettings" size="1em" class="close-icon clickable">mdi-close</v-icon>
    </v-card-title>
    <v-card-text>
      <LanguageSettings class="border mb-4" />
      <KingdomsPicker class="border mb-4" />
      <ImageRecognitionSettings class="border" />
    </v-card-text>
    <div class="d-flex justify-end">
      <v-btn
        @click="writeSettingsToFile"
        class="clickable mr-4 mb-4"
        append-icon="mdi-content-save-cog-outline"
        >Save to file</v-btn
      >
    </div>
  </v-card>
</template>

<style scoped>
  .close-icon:hover {
    cursor: pointer;
  }
</style>
