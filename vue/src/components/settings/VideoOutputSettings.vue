<script setup>
  import { ref, computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();
  const playingVideoStream = ref(false);

  globalProperties.$eel
    .is_video_playing()()
    .then((response) => {
      playingVideoStream.value = response;
    });

  function toggleVideoStream() {
    const eelFunction = playingVideoStream.value
      ? globalProperties.$eel.stop_output_video
      : globalProperties.$eel.start_output_video;

    eelFunction()()
      .then(() => {
        state.showSuccess(
          `${playingVideoStream.value ? 'Stopped' : 'Started'} playing video output.`
        );
        playingVideoStream.value = !playingVideoStream.value;
      })
      .catch(() => {
        state.showError(
          `Error ${playingVideoStream.value ? 'stopping' : 'starting'} video output.`
        );
      });
  }

  const playVideoOutput = computed({
    get() {
      return settings.playVideoOutput;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          playVideoOutput: value,
        })()
        .then(() => {
          settings.setPlayVideoOutput(value);
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  const playAudioOutput = computed({
    get() {
      return settings.playAudioOutput;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          playAudioOutput: value,
        })()
        .then(() => {
          settings.setPlayAudioOutput(value);
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });
</script>

<template>
  <v-card flat>
    <v-card-title> Video Output </v-card-title>
    <v-card-subtitle>
      If you wish, you can display the video feed that's being used for the image recognition in a
      seperate window. It can be used to check the frame rate or to create a window capture in OBS
      if the other solutions do not work for you.
    </v-card-subtitle>
    <v-card-text class="mt-4">
      <div class="d-flex flex-column flex-md-row align-md-center">
        <v-btn @click="toggleVideoStream">
          {{ playingVideoStream ? 'Stop video output' : 'Start video output' }}
        </v-btn>
        <template v-if="playingVideoStream || playVideoOutput">
          <v-switch
            v-model="playVideoOutput"
            label="Start automatically"
            hide-details
            class="slider-width mt-3 ml-md-8 mt-md-0"
            color="primary"></v-switch>
          <v-switch
            v-model="playAudioOutput"
            label="Include audio"
            hide-details
            class="slider-width ml-md-2"
            color="primary"></v-switch>
        </template>
      </div>
    </v-card-text>
  </v-card>
</template>
