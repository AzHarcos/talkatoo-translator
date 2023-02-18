import { defineStore } from 'pinia';
import { mainGameKingdoms } from '../consts/availableKingdoms';

export const useSettings = defineStore('settings', {
  state: () => {
    return {
      inputLanguage: 'chinese_simplified',
      outputLanguage: 'english',
      activeKingdoms: [...mainGameKingdoms],
      woodedFirst: true,
      seasideFirst: false,
    };
  },
  actions: {
    setInputLanguage(inputLanguage) {
      this.inputLanguage = inputLanguage;
    },
    setOutputLanguage(outputLanguage) {
      this.outputLanguage = outputLanguage;
    },
    setActiveKingdoms(activeKingdoms) {
      this.activeKingdoms = [...activeKingdoms];
    },
    setWoodedFirst(woodedFirst) {
      this.woodedFirst = woodedFirst;
    },
    setSeasideFirst(seasideFirst) {
      this.seasideFirst = seasideFirst;
    },
  },
});
