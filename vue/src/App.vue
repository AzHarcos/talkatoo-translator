<script setup>
  import HelloWorld from './components/HelloWorld.vue'
  import TheWelcome from './components/TheWelcome.vue'

  import CascadeImg from './assets/images/Cascade.png'
  import SandImg from './assets/images/Sand.png'
  import LakeImg from './assets/images/Lake.png'
  import WoodedImg from './assets/images/Wooded.png'
  import LostImg from './assets/images/Lost.png'
  import MetroImg from './assets/images/Metro.png'
  import SnowImg from './assets/images/Snow.png'
  import SeasideImg from './assets/images/Seaside.png'
  import LuncheonImg from './assets/images/Luncheon.png'
  import BowsersImg from './assets/images/Bowsers.png'

  import { ref, reactive, computed } from "vue";

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
    Bowsers: BowsersImg
  });

  const state = reactive({
    moonsByKingdom: [],
    mentionedMoons: [],
    collectedMoons: [],
    selectedKingdom: "Cascade"
  });

  function getMoonsByKingdom() {
    eel.get_moons_by_kingdom()().then(response => {
        state.moonsByKingdom = response;
    });
  }
  function updateMoons() {
      eel.get_mentioned_moons()(response => {
          if (response.length > state.mentionedMoons.length) {
              const newlyMentionedMoons = response.slice(state.mentionedMoons.length - response.length)

              newlyMentionedMoons.forEach(possibleMoons => {
                  state.mentionedMoons.push(possibleMoons.map(moon => ({
                      ...moon,
                      index: state.mentionedMoons.length
                  })));
              });

              const latestMoon = response[response.length - 1][0];
              state.selectedKingdom = latestMoon.kingdom;

              setTimeout(scrollToTop, 10);
          }
      });
      eel.get_collected_moons()(response => {
          const definiteCollectedMoons = response.filter(possibleMoons => possibleMoons.length === 1).map(possibleMoons => possibleMoons[0]);
          const newlyCollectedMoons = definiteCollectedMoons.filter(moon => !isMoonCollected(moon));

          state.collectedMoons.push(...newlyCollectedMoons);
      });
  }
  function scrollToTop() {
      const card = document.querySelector('.card');
      if (card) {
          card.scrollTop = 0;
      }
  }
  function moonToString(moon) {
      return `${moon.id} - ${moon.english} - ${moon.chinese_traditional}`;
  }
  function selectKingdom(kingdom) {
      state.selectedKingdom = kingdom;
  }
  function moonsAreEqual(first, other) {
      return first && other && first.id === other.id && first.kingdom === other.kingdom;
  }
  function areMoonsPending(possibleMoons) {
      const hasCorrectKingdom = possibleMoons[0].kingdom === state.selectedKingdom;
      const hasUncollectedOptions = possibleMoons.some(moon => !isMoonCollected(moon));
      const indexIsNotCollected = !state.collectedMoons.some(moon => moon.index === possibleMoons[0].index);

      return hasCorrectKingdom && hasUncollectedOptions && indexIsNotCollected;
  }
  function isMoonCollected(moon) {
      return state.collectedMoons.some(m => moonsAreEqual(moon, m));
  }
  function isMoonUnmentioned(moon) {
      return !moon.is_story && !state.mentionedMoons.some(possibleMoons => possibleMoons.some(m => moonsAreEqual(moon, m)));
  }
  function getFilteredPossibleMoons(possibleMoons) {
      return possibleMoons.filter(moon => !collectedOrCorrectMoons.value.some(m => m.index !== moon.index && moonsAreEqual(moon, m)));
  }
  function getCorrectMoonOptional(possibleMoons) {
      return possibleMoons.length === 1 ? possibleMoons[0] : possibleMoons.find(moon => moon.correct);
  }
  function setMoonCollected(moon) {
      state.collectedMoons.push(moon);
  }
  function setMoonUncollected(moon) {
      state.collectedMoons = state.collectedMoons.filter(m => !moonsAreEqual(moon, m));
  }
  function markCorrectOption(index, optionIndex) {
      state.mentionedMoons[index][optionIndex].correct = true;
  }
  function undoCorrectOption(moon, index) {
      setMoonUncollected(moon);
      state.mentionedMoons[index] = state.mentionedMoons[index].map(({correct, ...val}) => val);
  }

  const selectedKingdomPendingMoons = computed(() => {
      return state.mentionedMoons.filter(areMoonsPending);
  });
  const selectedKingdomCollectedMoons = computed(() => {
      return state.collectedMoons.filter(moon => moon.kingdom === state.selectedKingdom);
  });
  const collectedOrCorrectMoons = computed(() => {
    console.log(selectedKingdomPendingMoons.value);
      const correctMoons = selectedKingdomPendingMoons.value.map(possibleMoons => possibleMoons.find(moon => moon.correct)).filter(moon => moon);
      return [...selectedKingdomCollectedMoons.value, ...correctMoons];
  });

  getMoonsByKingdom();
  setInterval(updateMoons, 1000);
</script>

<template>
  <div class="window" v-bind:style="{ backgroundImage: 'url(' + kingdoms[state.selectedKingdom] + ')' }">
    <div class="tabs">
      <div v-for="kingdom in Object.keys(kingdoms)" class="tab" :class="{'selected': kingdom === state.selectedKingdom}" @click="selectKingdom(kingdom)">
          {{ kingdom }}
      </div>
    </div>
    <div v-if="state.selectedKingdom && (selectedKingdomPendingMoons.length > 0 || selectedKingdomCollectedMoons.length > 0)" class="container">
      <div class="card">
        <div class="list-container">
          <div v-if="selectedKingdomPendingMoons.length > 0" class="list-wrapper">
            <div class="list-header">Pending Moons:</div>
            <ul class="list">
              <li v-for="possibleMoons in selectedKingdomPendingMoons" class="list-item">
                <template  v-if="getFilteredPossibleMoons(possibleMoons).length > 0">
                  <div v-if="getFilteredPossibleMoons(possibleMoons).length === 1">
                    <span @click="setMoonCollected(getFilteredPossibleMoons(possibleMoons)[0])">{{ moonToString(getFilteredPossibleMoons(possibleMoons)[0]) }}</span>
                  </div>
                  <template v-else>
                    <div v-if="getFilteredPossibleMoons(possibleMoons).some(moon => moon.correct)" class="list-item-content">
                      <span @click="setMoonCollected(getFilteredPossibleMoons(possibleMoons).find(moon => moon.correct))">{{ moonToString(getFilteredPossibleMoons(possibleMoons).find(moon => moon.correct)) }}</span>
                      <span @click="undoCorrectOption(getFilteredPossibleMoons(possibleMoons).find(moon => moon.correct), getFilteredPossibleMoons(possibleMoons).find(moon => moon.correct).index)" class="material-symbols-outlined">undo</span>
                    </div>
                    <template v-else>
                      <div>{{ getFilteredPossibleMoons(possibleMoons).length }} possible options:</div>
                      <ul>
                        <li v-for="(moon, optionIndex) in getFilteredPossibleMoons(possibleMoons)" class="moon-option">
                          <div class="list-item-content">
                            <span>{{ moonToString(moon) }}</span>
                            <span @click="markCorrectOption(moon.index, optionIndex)" class="material-symbols-outlined">check</span>
                          </div>
                        </li>
                      </ul>
                    </template>
                  </template>
                </template>
              </li>
            </ul>
          </div>
          <div v-if="selectedKingdomCollectedMoons.length > 0" class="list-wrapper">
            <div class="list-header">Collected Moons:</div>
            <ul class="list">
              <li v-for="moon in selectedKingdomCollectedMoons" :key="moon.kingdom + moon.id" class="list-item">
                <div v-if="isMoonUnmentioned(moon)" class="list-item-content">
                  <span>{{ moonToString(moon) }}</span>
                  <span class="material-symbols-outlined">close</span>
                </div>
                <span v-else @click="setMoonUncollected(moon)">{{ moonToString(moon) }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
