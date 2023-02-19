<script setup>
  import { useSettings } from '@/stores/settings';
  import ImageRecognitionSettings from './ImageRecognitionSettings.vue';
  import KingdomsPicker from './KingdomSettings.vue';
  import LanguageSettings from './LanguageSettings.vue';

  const settings = useSettings();
</script>

<template>
  <v-card flat>
    <v-card-title class="ml-1 py-4 text-h5">Settings</v-card-title>
    <v-card-text>
      <LanguageSettings class="border mb-4" />
      <KingdomsPicker class="border mb-4" />
      <ImageRecognitionSettings class="border" />
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .border {
    border: solid 1px white;
  }
</style>
