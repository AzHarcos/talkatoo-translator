import { defineStore } from 'pinia';
import { areMoonsEqual, getDisplayKingdoms } from '@/composables';
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
    removeMoonOptions(moon) {
      this.mentionedMoons = this.mentionedMoons
        .map((possibleMoons) =>
          possibleMoons.length === 1
            ? possibleMoons
            : possibleMoons.filter((m) => !areMoonsEqual(moon, m))
        )
        .filter((possibleMoons) => possibleMoons.length > 0);
    },
    addMentionedMoon(possibleMoons) {
      const possibleMoonsWithIndex = possibleMoons.map((moon) => ({
        ...moon,
        index: this.mentionedMoonCount,
      }));

      if (possibleMoons.length === 1) {
        this.removeMoonOptions(possibleMoons[0]);
      }

      this.mentionedMoons.push(possibleMoonsWithIndex);
      this.mentionedMoonCount++;
    },
    markCorrectOption(index, optionIndex) {
      const actualIndex = this.mentionedMoons.findIndex(
        (possibleMoons) => possibleMoons[0].index === index
      );
      if (actualIndex >= 0) {
        this.mentionedMoons[actualIndex] = this.mentionedMoons[actualIndex].splice(optionIndex, 1);
        this.removeMoonOptions(this.mentionedMoons[actualIndex][0]);
      }
    },
    addCollectedMoon(moon) {
      this.collectedMoons.push(moon);

      const firstOptionsIndex = this.mentionedMoons.findLastIndex(
        (possibleMoons) =>
          possibleMoons.length > 1 && possibleMoons.some((m) => areMoonsEqual(moon, m))
      );

      if (firstOptionsIndex >= 0) {
        this.mentionedMoons[firstOptionsIndex] = [moon];
      }

      this.removeMoonOptions(moon);
    },
    setMoonUncollected(moon) {
      this.collectedMoons = this.collectedMoons.filter((m) => !areMoonsEqual(moon, m));
    },
    deleteMoon(moon, deleteFromCollected) {
      if (deleteFromCollected) {
        this.setMoonUncollected(moon);
      }
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
      this.mentionedMoonCount = 0;
      this.showSuccess('The run has been reset.');
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
