<script setup>
  import { ref, computed } from 'vue';
  import { useSettings } from '@/stores/settings';
  import LanguagePicker from './LanguagePicker.vue';

  const settings = useSettings();

  const inputLanguage = ref('');
  const outputLanguage = ref('');
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
              v-model="inputLanguage"
              label="Input Language"
              preselected="chinese_simplified"
              pattern="Chinese" />
          </v-col>
          <v-col cols="12" sm="6">
            <LanguagePicker
              v-model="outputLanguage"
              label="Output Language"
              preselected="english" />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="activeKingdoms"
              label="Kingdom Selection"
              required></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6">
            <v-checkbox v-model="useCompactMode" label="Compact Mode"></v-checkbox>
          </v-col>
          <v-col cols="6">
            <v-checkbox v-model="useTraditionalMode" label="Traditional Mode"></v-checkbox>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>
p
