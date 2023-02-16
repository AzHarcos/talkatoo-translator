import { defineStore } from 'pinia';

export const useSettings = defineStore('settings', {
  state: () => {
    return {
      inputLanguage: 'ch_tra',
      outputLanguage: 'en',
      activeKingdoms: [
        'Cascade',
        'Sand',
        'Lake',
        'Wooded',
        'Lost',
        'Metro',
        'Snow',
        'Seaside',
        'Luncheon',
        'Bowsers',
      ],
      useCompactMode: false,
      useTraditionalMode: false,
    };
  },
  actions: {},
});
