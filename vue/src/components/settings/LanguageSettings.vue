<script setup>
  import LanguagePicker from './LanguagePicker.vue';

  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();

  function setInputLanguage(language) {
    globalProperties.$eel
      .set_translate_from(language)()
      .then(() => {
        settings.setInputLanguage(language);
      })
      .catch(() => {
        console.log('error setting language');
      });
  }

  function setOutputLanguage(language) {
    globalProperties.$eel
      .set_translate_to(language)()
      .then(() => {
        settings.setOutputLanguage(language);
      })
      .catch(() => {
        console.log('error setting language');
      });
  }
</script>

<template>
  <v-card flat>
    <v-card-title> Language settings </v-card-title>
    <v-card-subtitle
      >Set the language you're playing the game on (will be used for image recognition) and the
      language you want the moon names to be translated to.</v-card-subtitle
    >
    <v-card-text class="mt-4">
      <v-row>
        <v-col cols="12" sm="6">
          <LanguagePicker
            @input="setInputLanguage"
            label="Input Language"
            :preselected="settings.inputLanguage" />
        </v-col>
        <v-col cols="12" sm="6">
          <LanguagePicker
            @input="setOutputLanguage"
            label="Output Language"
            :preselected="settings.outputLanguage" />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
