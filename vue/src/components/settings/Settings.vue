<script setup>
  import { useSettings } from '@/stores/settings';
  import KingdomsPicker from './KingdomsPicker.vue';
  import LanguagePicker from './LanguagePicker.vue';

  const settings = useSettings();
</script>

<template>
  <v-card flat rounded="lg" style="opacity: 0.95">
    <v-card-title>Settings</v-card-title>
    <v-card-subtitle>Set variables for image recogniton and display preferences</v-card-subtitle>
    <v-card-text>
      <v-form>
        <v-row>
          <v-col cols="12" sm="6">
            <LanguagePicker
              @input="(language) => settings.setInputLanguage(language)"
              label="Input Language"
              :preselected="settings.inputLanguage"
              pattern="Chinese" />
          </v-col>
          <v-col cols="12" sm="6">
            <LanguagePicker
              @input="(language) => settings.setOutputLanguage(language)"
              label="Output Language"
              :preselected="settings.outputLanguage" />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <KingdomsPicker />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>
p
