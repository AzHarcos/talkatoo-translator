import { useStore } from './store';

export function isMoonCollected(moon) {
  const store = useStore();

  return store.collectedMoons.some((m) => areMoonsEqual(moon, m));
}

export function areMoonsEqual(first, other) {
  return first && other && first.id === other.id && first.kingdom === other.kingdom;
}

export function areMoonsPending(possibleMoons) {
  const store = useStore();

  const hasCorrectKingdom = possibleMoons[0].kingdom === store.selectedKingdom;
  const hasUncollectedOptions = possibleMoons.some((moon) => !isMoonCollected(moon));
  const correctMoon = possibleMoons.find((moon) => moon.correct);

  const hasNotBeenCollected = !store.collectedMoons.some(
    (moon) => moon.index === possibleMoons[0].index || areMoonsEqual(moon, correctMoon)
  );

  return hasCorrectKingdom && hasUncollectedOptions && hasNotBeenCollected;
}

export function moonToString(moon) {
  return `${moon.id} - ${moon.english} - ${moon.chinese_traditional}`;
}
