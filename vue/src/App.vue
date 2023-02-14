<script setup>
  import MoonList from './components/MoonList.vue';

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

  import { ref, reactive, computed } from 'vue';
  import { useStore } from './store';

  const store = useStore();

  const kingdoms = ref({
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
    eel
      .get_moons_by_kingdom()()
      .then((response) => {
        store.setMoonsByKingdom(response);
      });
  }

  function updateMoons() {
    eel.get_mentioned_moons()((response) => {
      if (response.length > store.mentionedMoons.length) {
        const newlyMentionedMoons = response.slice(store.mentionedMoons.length - response.length);

        newlyMentionedMoons.forEach((possibleMoons) => {
          const moonsWithIndex = possibleMoons.map((moon) => ({
            ...moon,
            index: store.mentionedMoons.length,
            correct: possibleMoons.length === 0,
          }));
          store.addMentionedMoons(moonsWithIndex);
        });

        const latestMoon = response[response.length - 1][0];
        selectKingdom(latestMoon.kingdom);

        setTimeout(scrollToTop, 10);
      }
    });
    eel.get_collected_moons()((response) => {
      const definiteCollectedMoons = response
        .filter((possibleMoons) => possibleMoons.length === 1)
        .map((possibleMoons) => possibleMoons[0]);
      const newlyCollectedMoons = definiteCollectedMoons.filter((moon) => !isMoonCollected(moon));

      store.addCollectedMoons(newlyCollectedMoons);
    });
  }

  function scrollToTop() {
    const card = document.querySelector('.card');
    if (card) {
      card.scrollTop = 0;
    }
  }

  function selectKingdom(kingdom) {
    store.setSelectedKingdom(kingdom);
  }

  getMoonsByKingdom();
  setInterval(updateMoons, 1000);
</script>

<template>
  <div
    class="window"
    v-bind:style="{ backgroundImage: 'url(' + kingdoms[store.selectedKingdom] + ')' }">
    <div class="tabs">
      <div
        v-for="kingdom in Object.keys(kingdoms)"
        class="tab"
        :class="{ selected: kingdom === store.selectedKingdom }"
        @click="selectKingdom(kingdom)">
        {{ kingdom }}
      </div>
    </div>
    <MoonList />
  </div>
</template>

<style scoped></style>
