<script setup>
  import { useSettings } from '@/stores/settings';
  import KingdomsPicker from './KingdomSettings.vue';
  import LanguageSettings from './LanguageSettings.vue';

  const settings = useSettings();
</script>

<template>
  <v-card flat>
    <v-card-title>Settings</v-card-title>
    <v-card-subtitle>Set variables for image recogniton and display preferences</v-card-subtitle>
    <v-card-text>
      <v-form>
        <LanguageSettings />
        <KingdomsPicker />
      </v-form>
    </v-card-text>
  </v-card>
</template>
p
