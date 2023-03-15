<script setup>
  import { useState } from '@/stores/state';
  import { moonToString } from '@/composables';
  import DeletableEntry from './DeletableEntry.vue';

  const props = defineProps({
    possibleMoons: Array,
  });

  const state = useState();
</script>

<template>
  <DeletableEntry v-if="possibleMoons.length === 1" :moon="possibleMoons[0]">
    <span
      @click="() => state.addCollectedMoon(possibleMoons[0])"
      class="clickable"
      v-html="moonToString(possibleMoons[0])"></span>
  </DeletableEntry>
  <template v-else>
    <DeletableEntry :moon="possibleMoons[0]">
        <div>{{ possibleMoons.length }} possible options:</div>
      </DeletableEntry>
      <ul>
        <li v-for="(moon, optionIndex) in possibleMoons" class="moon-option">
          <div class="list-item-content">
            <span v-html="moonToString(moon)"></span>
            <v-icon
              @click="() => state.markCorrectOption(moon.index, optionIndex)"
              icon="mdi-check"
              size="20"
              class="clickable ml-4"></v-icon>
          </div>
        </li>
      </ul>
  </template>
</template>
