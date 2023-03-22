<script setup>
  import LanguagePicker from './LanguagePicker.vue';

  import { ref } from 'vue';
  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const state = useState();
  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();

  const inputLanguageLoading = ref(false);
  const outputLanguageLoading = ref(false);

  function setInputLanguage(language) {
    inputLanguageLoading.value = true;
    globalProperties.$eel
      .write_settings_to_file({
        ...settings.$state,
        inputLanguage: language,
      })()
      .then(() => {
        settings.setInputLanguage(language);
        state.showSuccess('Updated game language.');
      })
      .catch(() => {
        state.showError('Error setting game language.');
      })
      .finally(() => {
        inputLanguageLoading.value = false;
      });
  }

  function setOutputLanguage(language) {
    outputLanguageLoading.value = true;
    globalProperties.$eel
      .write_settings_to_file({
        ...settings.$state,
        outputLanguage: language,
      })()
      .then(() => {
        settings.setOutputLanguage(language);
        state.showSuccess('Updated output language.');
      })
      .catch(() => {
        state.showError('Error setting output language.');
      })
      .finally(() => {
        outputLanguageLoading.value = false;
      });
  }
</script>

<template>
  <v-card flat>
    <v-card-title> Languages </v-card-title>
    <v-card-subtitle
      >Set the language you're playing the game on (will be used for image recognition) and the
      language you want the moon names to be translated to.</v-card-subtitle
    >
    <v-card-text class="mt-4">
      <v-row>
        <v-col cols="12" sm="6">
          <LanguagePicker
            @input="setInputLanguage"
            label="Game Language"
            :selected="settings.inputLanguage"
            :loading="inputLanguageLoading" />
        </v-col>
        <v-col cols="12" sm="6">
          <LanguagePicker
            @input="setOutputLanguage"
            label="Output Language"
            :selected="settings.outputLanguage"
            :loading="outputLanguageLoading" />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
