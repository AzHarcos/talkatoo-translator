<script setup>
  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { correctMoonOptional, moonToString } from '@/composables';

  const props = defineProps({
    possibleMoons: Array,
  });

  const state = useState();

  const correctMoon = computed(() => {
    return correctMoonOptional(props.possibleMoons);
  });
</script>

<template>
  <div v-if="possibleMoons.length === 1">
    <span
      @click="() => state.addCollectedMoon(possibleMoons[0])"
      class="clickable"
      v-html="moonToString(possibleMoons[0])"></span>
  </div>
  <template v-else>
    <div v-if="correctMoon" class="list-item-content">
      <span
        @click="() => state.addCollectedMoon(correctMoon)"
        class="clickable"
        v-html="moonToString(correctMoon)"></span>
      <v-icon
        @click="() => state.undoCorrectOption(correctMoon, correctMoon.index)"
        icon="mdi-restore"
        size="24"
        class="ml-4"></v-icon>
    </div>
    <template v-else>
      <div>{{ possibleMoons.length }} possible options:</div>
      <ul>
        <li v-for="(moon, optionIndex) in possibleMoons" class="moon-option">
          <div class="list-item-content">
            <span v-html="moonToString(moon)"></span>
            <v-icon
              @click="() => state.markCorrectOption(moon.index, optionIndex)"
              icon="mdi-check"
              size="24"
              class="ml-4"></v-icon>
          </div>
        </li>
      </ul>
    </template>
  </template>
</template>
