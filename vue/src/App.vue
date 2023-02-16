<script setup>
  import MoonList from '@/components/moon-list/MoonList.vue';
  import Settings from '@/components/settings/Settings.vue';

  import useCurrentInstance from '@/hooks/useCurrentInstance';

  import CascadeImg from './assets/images/Cascade.png';
  import SandImg from './assets/images/Sand.png';
  import LakeImg from './assets/images/Lake.png';
  import WoodedImg from './assets/images/Wooded.png';
  import LostImg from './assets/images/Lost.png';
  import MetroImg from './assets/images/Metro.png';
  import SnowImg from './assets/images/Snow.png';
  import SeasideImg from './assets/images/Seaside.png';
  import LuncheonImg from './assets/images/Luncheon.png';
  import BowsersImg from './assets/images/Bowsers.png';

  import { ref } from 'vue';
  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import { isMoonCollected } from '@/composables';
  import { storeToRefs } from 'pinia';

  const state = useState();
  const settings = useSettings();

  const { selectedKingdom } = storeToRefs(state);

  const { globalProperties } = useCurrentInstance();

  const showSettings = ref(false);

  const kingdomImages = ref({
    Cascade: CascadeImg,
    Sand: SandImg,
    Lake: LakeImg,
    Wooded: WoodedImg,
    Lost: LostImg,
    Metro: MetroImg,
    Snow: SnowImg,
    Seaside: SeasideImg,
    Luncheon: LuncheonImg,
    Bowsers: BowsersImg,
  });

  function getMoonsByKingdom() {
    globalProperties.$eel
      .get_moons_by_kingdom()()
      .then((response) => {
        state.setMoonsByKingdom(response);
      });
  }

  function updateMoons() {
    globalProperties.$eel.get_mentioned_moons()((response) => {
      if (response.length > state.mentionedMoons.length) {
        const newlyMentionedMoons = response.slice(state.mentionedMoons.length - response.length);

        newlyMentionedMoons.forEach((possibleMoons) => {
          const moonsWithIndex = possibleMoons.map((moon) => ({
            ...moon,
            index: state.mentionedMoons.length,
            correct: possibleMoons.length === 0,
          }));
          state.addMentionedMoons(moonsWithIndex);
        });

        const latestMoon = response[response.length - 1][0];
        selectKingdom(latestMoon.kingdom);

        setTimeout(scrollToTop, 10);
      }
    });
    globalProperties.$eel.get_collected_moons()((response) => {
      const definiteCollectedMoons = response
        .filter((possibleMoons) => possibleMoons.length === 1)
        .map((possibleMoons) => possibleMoons[0]);
      const newlyCollectedMoons = definiteCollectedMoons.filter((moon) => !isMoonCollected(moon));

      if (newlyCollectedMoons.length === 0) return;

      const latestMoon = newlyCollectedMoons[newlyCollectedMoons.length - 1];
      selectKingdom(latestMoon.kingdom);

      state.addCollectedMoons(newlyCollectedMoons);
    });
  }

  function scrollToTop() {
    const card = document.querySelector('.card');
    if (card) {
      card.scrollTop = 0;
    }
  }

  function selectKingdom(kingdom) {
    state.setSelectedKingdom(kingdom);
  }

  getMoonsByKingdom();
  setInterval(updateMoons, 1000);
</script>

<template>
  <v-app>
    <v-app-bar color="primary" flat density="compact">
      <v-tabs v-model="selectedKingdom" grow>
        <v-tab v-for="kingdom in settings.activeKingdoms" :key="kingdom" :value="kingdom">
          {{ kingdom }}
        </v-tab>
      </v-tabs>
    </v-app-bar>
    <v-main>
      <v-container
        fluid
        class="image-container pa-8"
        :style="{ backgroundImage: 'url(' + kingdomImages[selectedKingdom] + ')' }">
        <v-row justify="end">
          <v-icon
            @click="showSettings = !showSettings"
            icon="mdi-cog"
            color="primary"
            size="50"
            class="mr-2 mb-2"></v-icon>
        </v-row>
        <v-row justify="center">
          <v-col cols="12" :style="{ 'max-width': showSettings ? '1400px' : '1000px' }">
            <Settings v-if="showSettings" /> <MoonList v-else />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
