<script setup>
  import { computed } from 'vue';
  import { useStore } from '../store';
  import { moonToString } from '../composables';

  const props = defineProps({
    possibleMoons: Array,
  });

  const store = useStore();

  const correctMoonOptional = computed(() => {
    return props.possibleMoons.find((moon) => moon.correct);
  });
</script>

<template>
  <div v-if="possibleMoons.length === 1">
    <span @click="store.setMoonCollected(possibleMoons[0])">{{
      moonToString(possibleMoons[0])
    }}</span>
  </div>
  <template v-else>
    <div v-if="correctMoonOptional" class="list-item-content">
      <span @click="store.setMoonCollected(correctMoonOptional)">{{
        moonToString(correctMoonOptional)
      }}</span>
      <span
        @click="store.undoCorrectOption(correctMoonOptional, correctMoonOptional.index)"
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
              @click="store.markCorrectOption(moon.index, optionIndex)"
              class="material-symbols-outlined"
              >check</span
            >
          </div>
        </li>
      </ul>
    </template>
  </template>
</template>
