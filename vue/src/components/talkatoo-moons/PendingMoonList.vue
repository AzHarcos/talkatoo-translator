<script setup>
  import PendingMoonEntry from './PendingMoonEntry.vue';

  import { useState } from '@/stores/state';
  import { padStart } from '@/composables';

  const props = defineProps({
    moons: Array,
  });

  const state = useState();
</script>

<template>
  <div class="list-wrapper">
    <div class="list-header">
      <span>Pending Moons:</span>
      <div><span v-html="padStart(moons.length.toString())"></span>/3</div>
    </div>
    <ul class="list">
      <li v-for="possibleMoons in moons" class="list-item">
        <PendingMoonEntry :possible-moons="possibleMoons" />
      </li>
    </ul>
  </div>
</template>
