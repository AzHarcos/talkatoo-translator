import { useState } from '@/stores/state';
import { useSettings } from '@/stores/settings';
import availableKingdoms from '@/consts/availableKingdoms';

function swapKingdoms(kingdoms, firstName, otherName) {
  const firstIndex = kingdoms.findIndex((kingdom) => kingdom.name === firstName);
  const otherIndex = kingdoms.findIndex((kingdom) => kingdom.name === otherName);

  const firstKingdom = kingdoms[firstIndex];

  kingdoms[firstIndex] = kingdoms[otherIndex];
  kingdoms[otherIndex] = firstKingdom;

  return kingdoms;
}

export function getDisplayKingdoms() {
  const settings = useSettings();
  let kingdoms = [...availableKingdoms];

  if (!settings.includePostGame) {
    kingdoms = kingdoms.filter((kingdom) => !kingdom.isPostGame);
  }

  if (!settings.includeWithoutTalkatoo) {
    kingdoms = kingdoms.filter((kingdom) => kingdom.hasTalkatoo);
  }

  if (!settings.woodedFirst) {
    kingdoms = swapKingdoms(kingdoms, 'Lake', 'Wooded');
  }

  if (settings.seasideFirst) {
    kingdoms = swapKingdoms(kingdoms, 'Snow', 'Seaside');
  }

  return kingdoms;
}

export function isMoonCollected(moon) {
  const state = useState();

  return state.collectedMoons.some((m) => areMoonsEqual(moon, m));
}

export function areMoonsEqual(first, other) {
  return first && other && first.id === other.id && first.kingdom === other.kingdom;
}

export function areMoonsPending(possibleMoons) {
  const state = useState();

  const hasCorrectKingdom = possibleMoons[0].kingdom === state.selectedKingdom.name;
  const hasUncollectedOptions = possibleMoons.some((moon) => !isMoonCollected(moon));
  const correctMoon = possibleMoons.find((moon) => moon.correct);

  const hasNotBeenCollected = !state.collectedMoons.some(
    (moon) => moon.index === possibleMoons[0].index || areMoonsEqual(moon, correctMoon)
  );

  return hasCorrectKingdom && hasUncollectedOptions && hasNotBeenCollected;
}

export function moonToString(moon) {
  const settings = useSettings();

  return `${padStart(moon.id.toString())} - ${moon[settings.outputLanguage]} - ${
    moon[settings.inputLanguage]
  }`;
}

export function padStart(str) {
  if (str.length === 2) return str;

  return `&nbsp&nbsp${str}`;
}

export function scrollToTop() {
  const mainContent = document.querySelector('.main-content');
  if (mainContent) {
    mainContent.scrollTop = 0;
  }
}

export function scrollToBottom() {
  const mainContent = document.querySelector('.main-content');
  if (mainContent) {
    mainContent.scrollTop = mainContent.scrollHeight;
  }
}
