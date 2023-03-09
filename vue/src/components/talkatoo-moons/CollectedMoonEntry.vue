<script setup>
  import { useState } from '../../stores/state';
  import { moonToString } from '../../composables';
  import MoonEntry from './MoonEntry.vue';

  const props = defineProps({
    moon: Object,
  });

  const state = useState();
</script>

<template>
  <MoonEntry :moon="moon">
    <span
      v-if="!moon.is_story && state.selectedKingdom.hasTalkatoo"
      @click="() => state.setMoonUncollected(moon)"
      class="clickable"
      v-html="moonToString(moon)"></span>
    <span v-else v-html="moonToString(moon)"></span>
  </MoonEntry>
</template>
