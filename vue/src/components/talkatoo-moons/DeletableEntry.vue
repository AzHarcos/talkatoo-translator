<script setup>
  import { useState } from '../../stores/state';
  import { useSettings } from '../../stores/settings';
  import { ref } from 'vue';

  const props = defineProps({
    moon: Object,
    isCollected: Boolean,
  });

  const state = useState();
  const settings = useSettings();

  const initiallyShowImage = !props.isCollected && settings.automaticallyShowImages;
  const showImage = ref(initiallyShowImage);

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
            v-if="moon.kingdom !== 'Darker'"
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
        rel="preload" />
    </template>
  </v-hover>
</template>

<style scoped>
  img {
    width: 300px;
  }
</style>
