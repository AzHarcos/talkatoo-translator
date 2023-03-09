<script setup>
  import { useState } from '../../stores/state';

  const props = defineProps({
    moon: Object,
  });

  const state = useState();

  function deleteMoon() {
    state.deleteMoon(props.moon);
  }
</script>

<template>
  <v-hover>
    <template v-slot:default="{ isHovering, props }">
      <div class="d-flex">
        <div v-bind="props" class="d-flex flex-grow-1">
          <slot></slot>
          <v-icon
            v-if="isHovering"
            @click="deleteMoon"
            icon="mdi-delete"
            class="clickable ml-2"
            size="20"></v-icon>
        </div>
        <slot name="tooltip"></slot>
      </div>
    </template>
  </v-hover>
</template>
