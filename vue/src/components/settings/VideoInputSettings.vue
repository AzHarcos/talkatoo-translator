<script setup>
  import { ref, computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { DEBUG_IMAGE_PATH } from '../../consts/filePaths';

  const { globalProperties } = useCurrentInstance();

  const state = useState();
  const settings = useSettings();

  const videoDevices = ref([]);
  const selectedDevice = ref(undefined);
  const showImage = ref(false);
  const debugImageUrl = ref('');

  function scrollToTitle() {
    setTimeout(() => {
      const scrollContainer = document.querySelector('.scroll-container');
      const title = document.getElementById('card');
      if (scrollContainer && title) {
        scrollContainer.scrollTop = title.offsetTop - 16;
      }
    }, 100);
  }

  globalProperties.$eel
    .get_video_devices()()
    .then((response) => {
      if (!response || response.length === 0) {
        return;
      }

      videoDevices.value = response;

      if (!settings.videoDevice) {
        selectedDevice.value = response[0];
        setVideoDevice(response[0], true);
        return;
      }

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

  function setVideoDevice(device, keepImageHidden) {
    if (!keepImageHidden) {
      showImage.value = true;
      scrollToTitle();
      debugImageUrl.value = '';
    }

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
    scrollToTitle();
    debugImageUrl.value = '';

    globalProperties.$eel
      .reset_borders()()
      .then((response) => {
        if (response) {
          debugImageUrl.value = DEBUG_IMAGE_PATH;
        } else {
          state.showError(`Error creating preview image.`);
        }
      })
      .catch(() => {
        state.showError(`Error creating preview image.`);
      });
  }
</script>

<template>
  <v-card flat id="card">
    <v-card-title> Video Input </v-card-title>
    <v-card-subtitle>
      Select your capture card as the input video device and test if it's setup properly. Using OBS
      Virtual Camera is NOT recommended due to compatibility and image quality issues. Consider
      using the Video Output settings instead.
    </v-card-subtitle>
    <v-card-text class="mt-4">
      <v-row align="center">
        <v-col cols="12" md="6">
          <v-autocomplete
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
        <v-col cols="6" md="3">
          <div class="d-flex">
            <v-btn @click="resetBorders" class="clickable mr-6">Show preview image</v-btn>
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
