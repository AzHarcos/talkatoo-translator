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

export function isMoonMentioned(moon) {
  const state = useState();

  return state.mentionedMoons.some((possibleMoons) =>
    areMoonsEqual(moon, correctMoonOptional(possibleMoons))
  );
}

export function isMoonCollected(moon) {
  const state = useState();

  return state.collectedMoons.some((m) => areMoonsEqual(moon, m));
}

export function correctMoonOptional(possibleMoons) {
  return possibleMoons.length === 1 ? possibleMoons[0] : undefined;
}

export function areMoonsEqual(first, other) {
  return first && other && first.id === other.id && first.kingdom === other.kingdom;
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
  const scrollContainer = document.querySelector('.scroll-container');
  if (scrollContainer) {
    scrollContainer.scrollTop = 0;
  }
}

export function scrollToBottom() {
  const scrollContainer = document.querySelector('.scroll-container');
  if (scrollContainer) {
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
  }
}
