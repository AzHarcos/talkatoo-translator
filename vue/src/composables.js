export function isMoonCollected(moon) {
    return store.collectedMoons.some(m => moonsAreEqual(moon, m));
}

export function areMoonsEqual(first, other) {
    return first && other && first.id === other.id && first.kingdom === other.kingdom;
}

export function areMoonsPending(possibleMoons) {
    const hasCorrectKingdom = possibleMoons[0].kingdom === store.selectedKingdom;
    const hasUncollectedOptions = possibleMoons.some(moon => !isMoonCollected(moon));
    const indexIsNotCollected = !store.collectedMoons.some(moon => moon.index === possibleMoons[0].index);

    return hasCorrectKingdom && hasUncollectedOptions && indexIsNotCollected;
}

export function getCorrectMoonOptional(possibleMoons) {
    return possibleMoons.length === 1 ? possibleMoons[0] : possibleMoons.find(moon => moon.correct);
}

export function moonToString(moon) {
    return `${moon.id} - ${moon.english} - ${moon.chinese_traditional}`;
}