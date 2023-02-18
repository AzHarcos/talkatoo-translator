<script setup>
  import { ref, computed, watch } from 'vue';
  import { useSettings } from '@/stores/settings';
  import { mainGameKingdoms, availableKingdoms } from '../../consts/availableKingdoms';

  const settings = useSettings();

  const kingdomPresets = ['Any%', 'Postgame'];

  const selectedKingdoms = ref([...mainGameKingdoms]);
  const selectedPreset = ref(kingdomPresets[0]);

  const woodedFirst = computed({
    get() {
      return settings.woodedFirst;
    },
    set(value) {
      console.log(value);
      settings.setWoodedFirst(value);
      swapKingdoms('Lake', 'Wooded');
    },
  });

  const seasideFirst = computed({
    get() {
      return settings.seasideFirst;
    },
    set(value) {
      console.log(value);
      settings.setSeasideFirst(value);
      swapKingdoms('Snow', 'Seaside');
    },
  });

  watch(selectedPreset, (preset) => {
    if (preset === 'Postgame') {
      selectedKingdoms.value = [...availableKingdoms];
    } else {
      selectedKingdoms.value = [...mainGameKingdoms];
    }

    if (!settings.woodedFirst) {
      swapKingdoms('Lake', 'Wooded');
    }

    if (settings.seasideFirst) {
      swapKingdoms('Snow', 'Seaside');
    }

    settings.setActiveKingdoms(selectedKingdoms.value);
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
  <v-row>
    <v-col cols="6">
      <v-autocomplete
        v-model="selectedPreset"
        label="Kingdom Selection"
        :items="kingdomPresets"></v-autocomplete>
    </v-col>
    <v-col cols="3">
      <v-switch v-model="woodedFirst" label="Wooded first"></v-switch>
    </v-col>
    <v-col cols="3">
      <v-switch v-model="seasideFirst" label="Seaside first"></v-switch>
    </v-col>
  </v-row>
</template>
