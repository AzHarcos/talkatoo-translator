import { defineStore } from 'pinia';
import { areMoonsEqual } from '@/composables';
import { getDisplayKingdoms } from '../composables';
import availableKingdoms from '../consts/availableKingdoms';

export const useState = defineStore('state', {
  state: () => {
    return {
      showSettings: false,
      moonsByKingdom: [],
      mentionedMoons: [],
      mentionedMoonCount: 0,
      collectedMoons: [],
      displayedKingdoms: [...availableKingdoms],
      currentKingdomName: undefined,
      selectedKingdom: availableKingdoms.find((kingdom) => kingdom.name === 'Cascade'),
      snackbar: {
        visible: false,
        text: '',
        color: 'black',
      },
    };
  },
  actions: {
    setShowSettings(showSettings) {
      this.showSettings = showSettings;
    },
    setMoonsByKingdom(moonsByKingdom) {
      this.moonsByKingdom = moonsByKingdom;
    },
    addMentionedMoon(possibleMoons) {
      const possibleMoonsWithIndex = possibleMoons.map((moon) => ({
        ...moon,
        index: this.mentionedMoonCount,
      }));
      this.mentionedMoons.push(possibleMoonsWithIndex);
      this.mentionedMoonCount++;
    },
    markCorrectOption(index, optionIndex) {
      const actualIndex = this.mentionedMoons.findIndex(
        (possibleMoons) => possibleMoons[0].index === index
      );
      if (actualIndex >= 0) {
        this.mentionedMoons[actualIndex][optionIndex].correct = true;
      }
    },
    undoCorrectOption(moon, index) {
      const actualIndex = this.mentionedMoons.findIndex(
        (possibleMoons) => possibleMoons[0].index === index
      );
      if (actualIndex >= 0) {
        this.setMoonUncollected(moon);
        this.mentionedMoons[actualIndex] = this.mentionedMoons[actualIndex].map(
          ({ correct, ...val }) => val
        );
      }
    },
    addCollectedMoon(moon) {
      this.collectedMoons.push(moon);
    },
    setMoonUncollected(moon) {
      this.collectedMoons = this.collectedMoons.filter((m) => !areMoonsEqual(moon, m));
    },
    deleteMoon(moon) {
      this.setMoonUncollected(moon);
      this.mentionedMoons = this.mentionedMoons.filter(
        (possibleMoons) => possibleMoons[0].index !== moon.index
      );
    },
    setCurrentKingdomName(currentKingdomName) {
      this.currentKingdomName = currentKingdomName;
    },
    setSelectedKingdom(kingdom) {
      this.selectedKingdom = kingdom;
    },
    updateKingdoms() {
      this.displayedKingdoms = getDisplayKingdoms();
    },
    resetRun() {
      this.mentionedMoons = [];
      this.collectedMoons = [];
      this.selectedKingdom = this.displayedKingdoms[0];
      this.showSuccess('Resetted the run.');
    },
    showSuccess(text) {
      this.snackbar.text = text;
      this.snackbar.color = 'black';
      this.snackbar.visible = true;
    },
    showError(text) {
      this.snackbar.text = text;
      this.snackbar.color = 'error';
      this.snackbar.visible = true;
    },
    closeSnackbar() {
      this.snackbar.visible = false;
    },
  },
});
