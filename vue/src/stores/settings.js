import { defineStore } from 'pinia';
import { mainGameKingdoms } from '../consts/availableKingdoms';

export const useSettings = defineStore('settings', {
  state: () => {
    return {
      inputLanguage: 'chinese_simplified',
      outputLanguage: 'english',
      activeKingdoms: [...mainGameKingdoms],
      includePostGame: false,
      woodedFirst: true,
      seasideFirst: false,
      isHardcore: false,
      videoDevice: undefined,
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
    setIncludePostGame(includePostGame) {
      this.includePostGame = includePostGame;
    },
    setWoodedFirst(woodedFirst) {
      this.woodedFirst = woodedFirst;
    },
    setSeasideFirst(seasideFirst) {
      this.seasideFirst = seasideFirst;
    },
    setIsHardcore(isHardcore) {
      this.isHardcore = isHardcore;
    },
    setVideoDevice(videoDevice) {
      this.videoDevice = videoDevice;
    },
  },
});
