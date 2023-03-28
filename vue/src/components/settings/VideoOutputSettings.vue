<script setup>
  import { ref, computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();
  const audioDevices = ref([]);
  const selectedAudioDevice = ref(undefined);
  const playingVideoStream = ref(false);
  const playingAudio = ref(false);

  function loadAudioDevices() {
    globalProperties.$eel
      .get_audio_devices()()
      .then((response) => {
        if (!response || response.length === 0) {
          return;
        }

        audioDevices.value = response;

        if (!settings.audioDevice) {
          selectedAudioDevice.value = response[0];
          setAudioDevice(response[0]);
          return;
        }

        const currentDevice = response.find(
          (device) => device.device_name === settings.audioDevice.device_name
        );

        if (!currentDevice) return;

        if (currentDevice.index === settings.audioDevice.index) {
          selectedAudioDevice.value = currentDevice;
          return;
        }

        settings.setAudioDevice({
          device_name: currentDevice.device_name,
          index: currentDevice.index,
        });
        selectedAudioDevice.value = settings.audioDevice;
      })
      .catch(() => state.showError('Error getting list of audio devices.'));
  }

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

  function setAudioDevice(device) {
    globalProperties.$eel
      .write_settings_to_file({
        ...settings.$state,
        audioDevice: device,
      })()
      .then((success) => {
        if (success) {
          settings.setAudioDevice(device);
        } else {
          selectedAudioDevice.value = undefined;
          state.showError('Error setting audio device.');
          document.activeElement.blur();
        }
      })
      .catch(() => {
        selectedAudioDevice.value = undefined;
        state.showError('Error setting audio device.');
        document.activeElement.blur();
      });
  }

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

  loadAudioDevices();
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
      <v-row align="center">
        <v-col cols="12" md="6">
          <v-autocomplete
            v-model="selectedAudioDevice"
            @click="loadAudioDevices"
            @update:model-value="setAudioDevice"
            label="Audio Device"
            :items="audioDevices"
            item-value="index"
            item-title="device_name"
            hide-details
            return-object
            class="clickable"></v-autocomplete>
        </v-col>
        <div class="d-flex flex-wrap align-center">
          <v-btn @click="toggleVideoStream" class="ml-6">
            {{ playingVideoStream ? 'Stop video output' : 'Start video output' }}
          </v-btn>
          <v-btn @click="toggleAudio" class="mx-6">
            {{ playingAudio ? 'Mute audio' : 'Play audio' }}
          </v-btn>
          <v-switch
            v-model="autoPlayOutputStreams"
            label="Play on startup"
            hide-details
            color="primary"></v-switch>
        </div>
      </v-row>
    </v-card-text>
  </v-card>
</template>
