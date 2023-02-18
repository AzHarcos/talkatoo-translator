import { useState } from '@/stores/state';
import { useSettings } from '@/stores/settings';

export function isMoonCollected(moon) {
  const state = useState();

  return state.collectedMoons.some((m) => areMoonsEqual(moon, m));
}

export function areMoonsEqual(first, other) {
  return first && other && first.id === other.id && first.kingdom === other.kingdom;
}

export function areMoonsPending(possibleMoons) {
  const state = useState();

  const hasCorrectKingdom = possibleMoons[0].kingdom === state.selectedKingdom;
  const hasUncollectedOptions = possibleMoons.some((moon) => !isMoonCollected(moon));
  const correctMoon = possibleMoons.find((moon) => moon.correct);

  const hasNotBeenCollected = !state.collectedMoons.some(
    (moon) => moon.index === possibleMoons[0].index || areMoonsEqual(moon, correctMoon)
  );

  return hasCorrectKingdom && hasUncollectedOptions && hasNotBeenCollected;
}

export function moonToString(moon) {
  const settings = useSettings();

  return `${moon.id} - ${moon[settings.outputLanguage]} - ${moon[settings.inputLanguage]}`;
}
