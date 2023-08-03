<script setup>
  import { useState } from '../../stores/state';
  import { ref } from 'vue';

  const props = defineProps({
    moon: Object,
    isCollected: Boolean,
  });

  const state = useState();

  const showImage = ref(false);
  const showOverlay = ref(false);

  function deleteMoon() {
    state.deleteMoon(props.moon, props.isCollected);
  }
</script>

<template>
  <v-hover>
    <template v-slot:default="{ isHovering, props }">
      <div class="d-flex">
        <div v-bind="props" class="d-flex flex-grow-1">
          <slot></slot>
          <v-icon
            @click="showImage = !showImage"
            :icon="showImage ? 'mdi-eye-off' : 'mdi-eye'"
            class="clickable ml-3"
            size="20"></v-icon>
          <v-icon
            v-if="isHovering"
            @click="deleteMoon"
            icon="mdi-delete"
            class="clickable ml-2"
            size="20"></v-icon>
        </div>
        <slot name="tooltip"></slot>
      </div>
      <img
        v-show="showImage"
        class="ma-4"
        :src="`http://localhost:8083/assets/moons/${moon.kingdom}/${moon.id}.png`"
        rel="preload"
        @click="showOverlay = true" />
      <v-overlay v-model="showOverlay" class="justify-center align-center" width="60%">
        <v-img
          :src="`http://localhost:8083/assets/moons/${moon.kingdom}/${moon.id}.png`"
          cover></v-img>
      </v-overlay>
    </template>
  </v-hover>
</template>

<style scoped>
  img {
    width: 350px;
  }
</style>
