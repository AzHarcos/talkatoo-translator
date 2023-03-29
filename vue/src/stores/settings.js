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
      windowCaptureCropping: [0, 0, 0, 0],
      videoDevice: undefined,
      audioDevice: undefined,
      autoPlayOutputStreams: false,
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
    setSkipResetConfirmation(skipResetConfirmation) {
      this.skipResetConfirmation = skipResetConfirmation;
    },
    setUseWindowCapture(useWindowCapture) {
      this.useWindowCapture = useWindowCapture;
    },
    setWindowCaptureName(windowCaptureName) {
      this.windowCaptureName = windowCaptureName;
    },
    setWindowCaptureCropping(windowCaptureCropping) {
      this.windowCaptureCropping = windowCaptureCropping;
    },
    setVideoDevice(videoDevice) {
      this.videoDevice = videoDevice;
    },
    setAudioDevice(audioDevice) {
      this.audioDevice = audioDevice;
    },
    setAutoPlayOutputStreams(autoPlayOutputStreams) {
      this.autoPlayOutputStreams = autoPlayOutputStreams;
    },
    setSettings(settings) {
      this.setInputLanguage(settings.inputLanguage);
      this.setOutputLanguage(settings.outputLanguage);
      this.setIncludePostGame(settings.includePostGame);
      this.setIncludeWithoutTalkatoo(settings.includeWithoutTalkatoo);
      this.setWoodedFirst(settings.woodedFirst);
      this.setSeasideFirst(settings.seasideFirst);
      this.setIsHardcore(settings.isHardcore);
      this.setSkipResetConfirmation(settings.skipResetConfirmation);
      this.setUseWindowCapture(settings.useWindowCapture);
      this.setWindowCaptureName(settings.windowCaptureName);
      this.setWindowCaptureCropping(settings.windowCaptureCropping);
      this.setVideoDevice(settings.videoDevice);
      this.setAudioDevice(settings.audioDevice);
      this.setAutoPlayOutputStreams(settings.autoPlayOutputStreams);
    },
  },
});
