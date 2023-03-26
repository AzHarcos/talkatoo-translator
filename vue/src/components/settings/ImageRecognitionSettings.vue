<script setup>
  import { ref, computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { scrollToBottom } from '@/composables';
  import { DEBUG_IMAGE_PATH } from '../../consts/filePaths';

  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();

  const openWindowNames = ref([]);
  const videoDevices = ref([]);
  const selectedWindowCapture = ref(undefined);
  const selectedDevice = ref(undefined);
  const showImage = ref(false);
  const debugImageUrl = ref('');

  globalProperties.$eel
    .get_open_windows()()
    .then((response) => {
      if (!response || response.length === 0) {
        return;
      }

      openWindowNames.value = response.filter((window) => window.name).map((window) => window.name);

      if (!settings.windowCaptureName) return;

      const currentWindowCapture = response.find(
        (window) => window.name === settings.windowCaptureName
      );

      if (currentWindowCapture) {
        selectedWindowCapture.value = currentWindowCapture.name;
      }
    })
    .catch(() => state.showError('Error getting list of open windows.'));

  globalProperties.$eel
    .get_video_devices()()
    .then((response) => {
      if (!response || response.length === 0) {
        return;
      }

      videoDevices.value = response;

      if (!settings.videoDevice) return;

      const currentDevice = response.find(
        (device) => device.device_name === settings.videoDevice.device_name
      );

      if (!currentDevice) return;

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

  function setWindowCapture(windowName) {
    showImage.value = true;
    setTimeout(scrollToBottom, 100);
    debugImageUrl.value = '';

    globalProperties.$eel
      .write_settings_to_file({
        ...settings.$state,
        windowCaptureName: windowName,
      })()
      .then((success) => {
        if (success) {
          settings.setWindowCaptureName(windowName);
          debugImageUrl.value = DEBUG_IMAGE_PATH;
        } else {
          selectedWindowCapture.value = undefined;
          state.showError('Error starting window capture.');
          document.activeElement.blur();
        }
      })
      .catch(() => {
        selectedWindowCapture.value = undefined;
        state.showError('Error starting window capture.');
        document.activeElement.blur();
      });
  }

  function setVideoDevice(device) {
    showImage.value = true;
    setTimeout(scrollToBottom, 100);
    debugImageUrl.value = '';

    globalProperties.$eel
      .write_settings_to_file({
        ...settings.$state,
        videoDevice: device,
      })()
      .then((success) => {
        if (success) {
          settings.setVideoDevice(device);
          debugImageUrl.value = DEBUG_IMAGE_PATH;
        } else {
          selectedDevice.value = undefined;
          state.showError('Error setting video device.');
          document.activeElement.blur();
        }
      })
      .catch(() => {
        selectedDevice.value = undefined;
        state.showError('Error setting video device.');
        document.activeElement.blur();
      });
  }

  function resetBorders() {
    showImage.value = true;
    setTimeout(scrollToBottom, 100);
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

  const useWindowCapture = computed({
    get() {
      return settings.useWindowCapture;
    },
    set(value) {
      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          useWindowCapture: value,
        })()
        .then(() => {
          settings.setUseWindowCapture(value);
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });
</script>

<template>
  <v-card flat>
    <v-card-title> Image recognition </v-card-title>
    <v-card-subtitle>
      Select your capture card as the input video device and test if it's setup properly.
      <span v-if="openWindowNames.length > 0"
        >Alternatively you can use a window capture for the image recognition instead.</span
      >
    </v-card-subtitle>

    <v-card-text class="mt-4">
      <v-row align="center">
        <v-col cols="12" sm="6">
          <v-autocomplete
            v-if="settings.useWindowCapture"
            v-model="selectedWindowCapture"
            @update:model-value="setWindowCapture"
            label="Window Capture"
            :items="openWindowNames"
            hide-details
            class="clickable"></v-autocomplete>
          <v-autocomplete
            v-else
            v-model="selectedDevice"
            @update:model-value="setVideoDevice"
            label="Video Device"
            :items="videoDevices"
            item-value="index"
            item-title="device_name"
            hide-details
            return-object
            class="clickable"></v-autocomplete>
        </v-col>
        <v-col cols="6" sm="3">
          <div class="d-flex">
            <v-btn @click="resetBorders" class="clickable mr-6">Show preview image</v-btn>
            <v-btn @click="useWindowCapture = !useWindowCapture">
              {{ useWindowCapture ? 'Use video device' : 'Use window capture' }}
            </v-btn>
          </div>
        </v-col>
      </v-row>
      <v-img v-if="showImage" :src="debugImageUrl" aspect-ratio="1.7778" class="border mt-4">
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular color="grey-lighten-4" indeterminate></v-progress-circular>
          </div> </template
      ></v-img>
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .fixed-width {
    width: 300px;
    max-width: 300px;
  }
</style>
