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
    addMentionedMoons(possibleMoons) {
      this.mentionedMoons.push(possibleMoons);
    },
    markCorrectOption(index, optionIndex) {
      this.mentionedMoons[index][optionIndex].correct = true;
    },
    undoCorrectOption(moon, index) {
      this.setMoonUncollected(moon);
      this.mentionedMoons[index] = this.mentionedMoons[index].map(({ correct, ...val }) => val);
    },
    addCollectedMoons(moons) {
      this.collectedMoons.push(...moons);
    },
    setMoonCollected(moon) {
      this.collectedMoons.push(moon);
    },
    setMoonUncollected(moon) {
      this.collectedMoons = this.collectedMoons.filter((m) => !areMoonsEqual(moon, m));
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
