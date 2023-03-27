<script setup>
  import { ref, computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();
  const playingVideoStream = ref(false);
  const playingAudio = ref(false);

  globalProperties.$eel
    .is_video_playing()()
    .then((response) => {
      playingVideoStream.value = response;
    });

  globalProperties.$eel
    .is_audio_playing()()
    .then((response) => {
      playingAudio.value = response;
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

  function toggleAudio() {
    const eelFunction = playingAudio.value
      ? globalProperties.$eel.stop_output_audio
      : globalProperties.$eel.start_output_audio;

    eelFunction()()
      .then(() => {
        playingAudio.value = !playingAudio.value;
      })
      .catch(() => {
        state.showError(`Error ${playingAudio.value ? 'stopping' : 'starting'} audio.`);
      });
  }

  const autoPlayOutputStreams = computed({
    get() {
      return settings.autoPlayOutputStreams;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          autoPlayOutputStreams: value,
        })()
        .then(() => {
          settings.setAutoPlayOutputStreams(value);
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
    <v-card-text>
      <div class="d-flex flex-wrap align-center">
        <v-btn @click="toggleVideoStream">
          {{ playingVideoStream ? 'Stop video output' : 'Start video output' }}
        </v-btn>
        <v-btn @click="toggleAudio" class="mx-6">
          {{ playingAudio ? 'Mute audio' : 'Play audio' }}
        </v-btn>
        <v-switch
          v-model="autoPlayOutputStreams"
          label="Start automatically"
          hide-details
          color="primary"></v-switch>
      </div>
    </v-card-text>
  </v-card>
</template>
