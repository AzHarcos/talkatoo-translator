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
    <span @click="state.setMoonCollected(possibleMoons[0])">{{
      moonToString(possibleMoons[0])
    }}</span>
  </div>
  <template v-else>
    <div v-if="correctMoonOptional" class="list-item-content">
      <span @click="state.setMoonCollected(correctMoonOptional)">{{
        moonToString(correctMoonOptional)
      }}</span>
      <span
        @click="state.undoCorrectOption(correctMoonOptional, correctMoonOptional.index)"
        class="material-symbols-outlined"
        >undo</span
      >
    </div>
    <template v-else>
      <div>{{ possibleMoons.length }} possible options:</div>
      <ul>
        <li v-for="(moon, optionIndex) in possibleMoons" class="moon-option">
          <div class="list-item-content">
            <span>{{ moonToString(moon) }}</span>
            <span
              @click="state.markCorrectOption(moon.index, optionIndex)"
              class="material-symbols-outlined"
              >check</span
            >
          </div>
        </li>
      </ul>
    </template>
  </template>
</template>
