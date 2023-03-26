import { defineStore } from 'pinia';

export const useSettings = defineStore('settings', {
  state: () => {
    return {
      inputLanguage: 'chinese_traditional',
      outputLanguage: 'english',
      includePostGame: false,
      includeWithoutTalkatoo: false,
      woodedFirst: false,
      seasideFirst: false,
      isHardcore: false,
      skipResetConfirmation: false,
      useWindowCapture: false,
      windowCaptureName: undefined,
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
    setIncludePostGame(includePostGame) {
      this.includePostGame = includePostGame;
    },
    setIncludeWithoutTalkatoo(includeWithoutTalkatoo) {
      this.includeWithoutTalkatoo = includeWithoutTalkatoo;
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
    setUseWindowCapture(useWindowCapture) {
      this.useWindowCapture = useWindowCapture;
    },
    setWindowCaptureName(windowCaptureName) {
      this.windowCaptureName = windowCaptureName;
    },
    setVideoDevice(videoDevice) {
      this.videoDevice = videoDevice;
    },
    setSkipResetConfirmation(skipResetConfirmation) {
      this.skipResetConfirmation = skipResetConfirmation;
    },
    setSettings(settings) {
      this.setInputLanguage(settings.inputLanguage);
      this.setOutputLanguage(settings.outputLanguage);
      this.setIncludePostGame(settings.includePostGame);
      this.setIncludeWithoutTalkatoo(settings.includeWithoutTalkatoo);
      this.setWoodedFirst(settings.woodedFirst);
      this.setSeasideFirst(settings.seasideFirst);
      this.setIsHardcore(settings.isHardcore);
      this.setUseWindowCapture(settings.useWindowCapture);
      this.setWindowCaptureName(settings.windowCaptureName);
      this.setVideoDevice(settings.videoDevice);
      this.setSkipResetConfirmation(settings.skipResetConfirmation);
    },
  },
});
