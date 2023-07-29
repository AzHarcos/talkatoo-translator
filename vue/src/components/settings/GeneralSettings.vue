<script setup>
  import { computed } from 'vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { useDisplay } from 'vuetify/lib/framework.mjs';

  const state = useState();
  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();
  const { mdAndDown } = useDisplay();

  const isHardcore = computed({
    get() {
      return settings.isHardcore;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          isHardcore: value,
        })()
        .then(() => {
          settings.setIsHardcore(value);
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  const manuallySwitchKingdoms = computed({
    get() {
      return settings.manuallySwitchKingdoms;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          manuallySwitchKingdoms: value,
        })()
        .then(() => {
          settings.setManuallySwitchKingdoms(value);
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });
</script>

<template>
  <v-card flat>
    <v-card-title>General</v-card-title>
    <v-card-subtitle
      >Change general settings like the category you're playing (regular or hardcore) and whether
      the kingdoms should transition automatically or only manually.</v-card-subtitle
    >
    <v-card-text>
      <v-row :no-gutters="mdAndDown">
        <v-col cols="12" lg="6"
          ><v-switch
            v-model="isHardcore"
            label="Use hardcore (story moons don't count)"
            hide-details
            color="primary"></v-switch
        ></v-col>
        <v-col cols="12" lg="6"
          ><v-switch
            v-model="manuallySwitchKingdoms"
            label="Manually switch kingdoms (automatic transitions disabled)"
            hide-details
            color="primary"></v-switch
        ></v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style></style>
