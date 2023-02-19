<script setup>
  import { computed } from 'vue';
  import { useState } from '@/stores/state';
  import { moonToString } from '@/composables';

  const props = defineProps({
    possibleMoons: Array,
  });

  const state = useState();

  const correctMoonOptional = computed(() => {
    return props.possibleMoons.find((moon) => moon.correct);
  });
</script>

<template>
  <div v-if="possibleMoons.length === 1">
    <span @click="() => state.setMoonCollected(possibleMoons[0])" class="clickable">{{
      moonToString(possibleMoons[0])
    }}</span>
  </div>
  <template v-else>
    <div v-if="correctMoonOptional" class="list-item-content">
      <span @click="() => state.setMoonCollected(correctMoonOptional)" class="clickable">{{
        moonToString(correctMoonOptional)
      }}</span>
      <v-icon
        @click="() => state.undoCorrectOption(correctMoonOptional, correctMoonOptional.index)"
        icon="mdi-restore"
        size="24"
        class="ml-4"></v-icon>
    </div>
    <template v-else>
      <div>{{ possibleMoons.length }} possible options:</div>
      <ul>
        <li v-for="(moon, optionIndex) in possibleMoons" class="moon-option">
          <div class="list-item-content">
            <span>{{ moonToString(moon) }}</span>
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
