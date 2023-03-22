<script setup>
  import ImageRecognitionSettings from './ImageRecognitionSettings.vue';
  import KingdomsPicker from './KingdomSettings.vue';
  import LanguageSettings from './LanguageSettings.vue';

  import { useState } from '@/stores/state';

  const state = useState();

  function closeSettings() {
    state.setShowSettings(false);
  }
</script>

<template>
  <v-card flat>
    <v-card-title class="pt-4 d-flex justify-space-between">
      <div class="text-h5">Settings</div>
      <v-icon @click="closeSettings" size="1em" class="close-icon clickable">mdi-close</v-icon>
    </v-card-title>
    <v-card-subtitle>
      Set your preferences regarding languages, displayed kingdoms and image recognition. Settings
      will be saved automatically.
    </v-card-subtitle>
    <v-card-text>
      <LanguageSettings class="border mb-4" />
      <KingdomsPicker class="border mb-4" />
      <ImageRecognitionSettings class="border" />
    </v-card-text>
    <v-card-actions class="pa-4 pt-0">
      <v-btn @click="closeSettings" class="ml-auto clickable" variant="outlined"> Close </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
  .close-icon:hover {
    cursor: pointer;
  }
</style>
