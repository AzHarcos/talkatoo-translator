<script setup>
  import { ref, computed } from 'vue';
  import { useSettings } from '@/stores/settings';
  import { mainGameKingdoms, availableKingdoms } from '../../consts/availableKingdoms';

  const settings = useSettings();

  const selectedKingdoms = ref([...settings.activeKingdoms]);

  const includePostGame = computed({
    get() {
      return settings.includePostGame;
    },
    set(value) {
      settings.setIncludePostGame(value);

      selectedKingdoms.value = value ? [...availableKingdoms] : [...mainGameKingdoms];

      if (!settings.woodedFirst) {
        swapKingdoms('Lake', 'Wooded');
      }

      if (settings.seasideFirst) {
        swapKingdoms('Snow', 'Seaside');
      }

      settings.setActiveKingdoms(selectedKingdoms.value);
    },
  });

  const isHardcore = computed({
    get() {
      return settings.isHardcore;
    },
    set(value) {
      settings.setIsHardcore(value);
    },
  });

  const woodedFirst = computed({
    get() {
      return settings.woodedFirst;
    },
    set(value) {
      settings.setWoodedFirst(value);
      swapKingdoms('Lake', 'Wooded');
    },
  });

  const seasideFirst = computed({
    get() {
      return settings.seasideFirst;
    },
    set(value) {
      settings.setSeasideFirst(value);
      swapKingdoms('Snow', 'Seaside');
    },
  });

  function swapKingdoms(kingdom1, kingdom2) {
    const firstIndex = selectedKingdoms.value.findIndex(
      (kingdom) => kingdom === kingdom1 || kingdom === kingdom2
    );
    if (firstIndex === -1) return;

    const secondIndex = firstIndex + 1;
    const firstKingdom = selectedKingdoms.value[firstIndex];
    const secondKingdom = selectedKingdoms.value[secondIndex];

    selectedKingdoms.value[firstIndex] = secondKingdom;
    selectedKingdoms.value[secondIndex] = firstKingdom;

    settings.setActiveKingdoms(selectedKingdoms.value);
  }
</script>

<template>
  <v-card flat>
    <v-card-title>Kingdoms</v-card-title>
    <v-card-subtitle
      >Edit which kingdoms should be displayed and in which order you're planning to visit them.
      Post game kingdoms include Cap, Moon and Mushroom.</v-card-subtitle
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
