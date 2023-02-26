<script setup>
  import { computed } from 'vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';

  const state = useState();
  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();

  const includePostGame = computed({
    get() {
      return settings.includePostGame;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file(
          JSON.stringify({
            ...settings.$state,
            includePostGame: value,
          })
        )()
        .then(() => {
          settings.setIncludePostGame(value);
          state.updateKingdoms();
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  const includeWithoutTalkatoo = computed({
    get() {
      return settings.includeWithoutTalkatoo;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file(
          JSON.stringify({
            ...settings.$state,
            includeWithoutTalkatoo: value,
          })
        )()
        .then(() => {
          settings.setIncludeWithoutTalkatoo(value);
          state.updateKingdoms();
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  const isHardcore = computed({
    get() {
      return settings.isHardcore;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file(
          JSON.stringify({
            ...settings.$state,
            isHardcore: value,
          })
        )()
        .then(() => {
          settings.setIsHardcore(value);
          state.updateKingdoms();
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  const woodedFirst = computed({
    get() {
      return settings.woodedFirst;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file(
          JSON.stringify({
            ...settings.$state,
            isHardcore: value,
          })
        )()
        .then(() => {
          settings.setWoodedFirst(value);
          state.updateKingdoms();
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  const seasideFirst = computed({
    get() {
      return settings.seasideFirst;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file(
          JSON.stringify({
            ...settings.$state,
            isHardcore: value,
          })
        )()
        .then(() => {
          settings.setSeasideFirst(value);
          state.updateKingdoms();
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });
</script>

<template>
  <v-card flat>
    <v-card-title>Kingdoms</v-card-title>
    <v-card-subtitle
      >Select which kingdoms should be displayed and in what order. Post game kingdoms include
      kingdoms where you don't collect moons in Any%. Other kingdoms include kingdoms where Talkatoo
      is not present.</v-card-subtitle
    >
    <v-card-text>
      <div class="d-flex flex-column flex-lg-row justify-lg-space-between">
        <v-switch
          v-model="includePostGame"
          label="Include post game"
          hide-details
          class="slider-width"
          color="primary"></v-switch>
        <v-switch
          v-model="includeWithoutTalkatoo"
          label="Other kingdoms"
          hide-details
          class="slider-width"
          color="primary"></v-switch>
        <v-switch
          v-model="woodedFirst"
          label="Wooded first"
          hide-details
          class="slider-width"
          color="primary"></v-switch>
        <v-switch
          v-model="seasideFirst"
          label="Seaside first"
          hide-details
          class="slider-width"
          color="primary"></v-switch>
        <v-switch
          v-model="isHardcore"
          label="Hardcore?"
          hide-details
          class="slider-width"
          color="primary"></v-switch>
      </div>
    </v-card-text>
  </v-card>
</template>

<style>
  .slider-width {
    max-width: 220px;
  }
</style>
