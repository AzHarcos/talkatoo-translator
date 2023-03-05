<script setup>
  import { useState } from '../../stores/state';
  import { moonToString } from '../../composables';

  const props = defineProps({
    moon: Object,
  });

  const state = useState();
</script>

<template>
  <span
    v-if="!moon.is_story"
    @click="() => state.setMoonUncollected(moon)"
    class="clickable"
    v-html="moonToString(moon)"></span>
  <span v-else v-html="moonToString(moon)"></span>
</template>
