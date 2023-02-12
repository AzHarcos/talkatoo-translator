import { defineStore } from 'pinia'
import { areMoonsEqual } from './composables';

export const useStore = defineStore('store', {
  state: () => {
    return {
        moonsByKingdom: [],
        mentionedMoons: [],
        collectedMoons: [],
        selectedKingdom: "Cascade"
    }
  },
  actions: {
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
      this.mentionedMoons[index] = this.mentionedMoons[index].map(({correct, ...val}) => val);
    },
    addCollectedMoons(moons) {
      this.collectedMoons.push(...moons);
    },
    setMoonCollected(moon) {
      this.collectedMoons.push(moon);
    },
    setMoonUncollected(moon) {
      this.collectedMoons = this.collectedMoons.filter(m => !areMoonsEqual(moon, m));
    },
    setSelectedKingdom(kingdom) {
      this.selectedKingdom = kingdom;
    }
  }
})