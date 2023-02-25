<script setup>
  import { ref } from 'vue';
  import { useDisplay } from 'vuetify';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { scrollToBottom } from '@/composables';
  import { DEBUG_IMAGE_PATH } from '../../consts/filePaths';

  const { lgAndUp } = useDisplay();
  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();

  const videoDevices = ref([]);
  const selectedDevice = ref(undefined);
  const showImage = ref(false);
  const debugImageUrl = ref(DEBUG_IMAGE_PATH);

  globalProperties.$eel
    .get_video_devices()()
    .then((response) => {
      if (!response || response.length === 0) {
        return;
      }

      videoDevices.value = response;

      if (!settings.videoDevice) {
        selectedDevice.value = response[0];
        return;
      }

      const currentDevice = response.find(
        (device) => device.device_name === settings.videoDevice.device_name
      );

      if (currentDevice.index === settings.videoDevice.index) {
        selectedDevice.value = currentDevice;
        return;
      }

      settings.setVideoDevice({
        device_name: currentDevice.device_name,
        index: currentDevice.index,
      });
      selectedDevice.value = settings.videoDevice;
    })
    .catch(() => state.showError('Error getting video devices.'));

  function setVideoDevice(device) {
    // TODO: improve loading / scroll handling
    if (!showImage.value) {
      showImage.value = true;
      setTimeout(() => (debugImageUrl.value = ''), 100);
      setTimeout(scrollToBottom, 400);
    } else {
      scrollToBottom();
      debugImageUrl.value = '';
    }

    globalProperties.$eel
      .write_settings_to_file(
        JSON.stringify({
          ...settings.$state,
          videoDevice: device,
        })
      )()
      .then(() => {
        settings.setVideoDevice(device);
        debugImageUrl.value = DEBUG_IMAGE_PATH;
      })
      .catch(() => {
        selectedDevice.value = undefined;
        state.showError('Error setting video device.');
        document.activeElement.blur();
      });
  }

  function resetBorders() {
    // TODO: improve loading / scroll handling
    if (!showImage.value) {
      showImage.value = true;
      setTimeout(scrollToBottom, 400);
      return;
    }

    scrollToBottom();
    debugImageUrl.value = '';

    globalProperties.$eel
      .reset_borders()()
      .then((response) => {
        if (response) {
          debugImageUrl.value = DEBUG_IMAGE_PATH;
        } else {
          state.showError('Error resetting borders.');
        }
      })
      .catch(() => {
        state.showError('Error resetting borders.');
      });
  }
</script>

<template>
  <v-card flat>
    <v-card-title> Image recognition </v-card-title>
    <v-card-subtitle>
      Select your capture card as the input video device and test if it's setup properly.
    </v-card-subtitle>
    <v-card-text class="mt-4">
      <v-row v-if="lgAndUp" align="center">
        <v-col cols="3">
          <v-autocomplete
            v-model="selectedDevice"
            @update:model-value="setVideoDevice"
            label="Video device"
            :items="videoDevices"
            item-value="index"
            item-title="device_name"
            hide-details
            return-object
            class="clickable"></v-autocomplete>
        </v-col>
        <v-col cols="3">
          <v-btn @click="resetBorders" class="clickable">Show preview image</v-btn>
        </v-col>
      </v-row>
      <div v-else class="d-flex flex-column picker-width">
        <v-autocomplete
          v-model="selectedDevice"
          @update:model-value="setVideoDevice"
          label="Video device"
          :items="videoDevices"
          item-title="device_name"
          hide-details
          return-object
          class="clickable"></v-autocomplete>
        <v-btn @click="resetBorders" class="clickable mt-4">Show preview image</v-btn>
      </div>
      <v-img v-show="showImage" :src="debugImageUrl" class="border mt-4">
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular color="grey-lighten-4" indeterminate></v-progress-circular>
          </div> </template
      ></v-img>
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .picker-width {
    max-width: 300px;
  }
</style>
