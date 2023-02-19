<script setup>
  import { useSettings } from '@/stores/settings';
  import ImageRecognitionSettings from './ImageRecognitionSettings.vue';
  import KingdomsPicker from './KingdomSettings.vue';
  import LanguageSettings from './LanguageSettings.vue';

  const settings = useSettings();
</script>

<template>
  <v-card flat>
    <v-card-title>Settings</v-card-title>
    <v-card-text>
      <LanguageSettings />
      <KingdomsPicker />
      <ImageRecognitionSettings />
    </v-card-text>
  </v-card>
</template>
p
