<script setup>
  import { computed } from 'vue';

  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();

  const videoIndexOptions = [0, 1, 2]; //TODO: get from python

  const videoIndex = computed({
    get() {
      return settings.videoIndex;
    },
    set(index) {
      globalProperties.$eel
        .set_video_index(index)()
        .then(() => {
          settings.setVideoIndex(index);
        })
        .catch(() => {
          console.log('error setting video index');
        });
    },
  });

  function resetBorders() {
    globalProperties.$eel
      .reset_borders()()
      .then(() => {
        console.log('resetted borders'); // TODO: display test image
      })
      .catch(() => {
        console.log('error resetting borders');
      });
  }
</script>

<template>
  <v-card flat>
    <v-card-title> Image recognition settings </v-card-title>
    <v-card-subtitle
      >Set the video index of your capture card and test if the video feed is setup
      properly.</v-card-subtitle
    >
    <v-card-text>
      <v-row>
        <v-col cols="12" sm="6">
          <v-autocomplete
            v-model="videoIndex"
            :items="videoIndexOptions"
            label="Video index"></v-autocomplete>
        </v-col>
        <v-col cols="12" sm="6">
          <v-btn @click="resetBorders">Reset capture border</v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
