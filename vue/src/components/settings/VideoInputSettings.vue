<script setup>
  import { ref, computed } from 'vue';

  import { useState } from '@/stores/state';
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';
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
  const cropLeft = ref(settings.windowCaptureCropping[0]);
  const cropTop = ref(settings.windowCaptureCropping[1]);
  const cropRight = ref(settings.windowCaptureCropping[2]);
  const cropBottom = ref(settings.windowCaptureCropping[3]);

  function scrollToTitle() {
    setTimeout(() => {
      const scrollContainer = document.querySelector('.scroll-container');
      const title = document.getElementById('card');
      if (scrollContainer && title) {
        scrollContainer.scrollTop = title.offsetTop - 4;
      }
    }, 100);
  }

  function loadOpenWindows() {
    globalProperties.$eel
      .get_open_windows()()
      .then((response) => {
        if (!response || response.length === 0) {
          return;
        }

        openWindowNames.value = response
          .filter((window) => window.name)
          .map((window) => window.name);

        if (!settings.windowCaptureName) return;

        const currentWindowCapture = response.find(
          (window) => window.name === settings.windowCaptureName
        );

        if (currentWindowCapture) {
          selectedWindowCapture.value = currentWindowCapture.name;
        }
      })
      .catch(() => state.showError('Error getting list of open windows.'));
  }

    function loadVideoDevices() {
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
  }

  function setWindowCapture(windowName) {
    showImage.value = true;
    scrollToTitle();
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
          state.showError('Error starting window capture, make sure the window is not minimized.');
          document.activeElement.blur();
        }
      })
      .catch(() => {
        selectedWindowCapture.value = undefined;
        state.showError('Error starting window capture, make sure the window is not minimized.');
        document.activeElement.blur();
      });
  }

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

    if (settings.useWindowCapture) {
      const updatedCropping = [
        +cropLeft.value,
        +cropTop.value,
        +cropRight.value,
        +cropBottom.value,
      ];
      if (updatedCropping + '' !== settings.windowCaptureCropping + '') {
        globalProperties.$eel
          .write_settings_to_file({
            ...settings.$state,
            windowCaptureCropping: updatedCropping,
          })()
          .then((success) => {
            if (success) {
              debugImageUrl.value = DEBUG_IMAGE_PATH;
              settings.setWindowCaptureCropping(updatedCropping);
            } else {
              [cropLeft.value, cropTop.value, cropRight.value, cropBottom.value] =
                settings.windowCaptureCropping;
              state.showError(
                'Error creating preview image, please make sure to select valid cropping values.'
              );
            }
          })
          .catch(() => {
            [cropLeft.value, cropTop.value, cropRight.value, cropBottom.value] =
              settings.windowCaptureCropping;
            state.showError(
              'Error creating preview image, please make sure to select valid cropping values.'
            );
          });
        return;
      }
    }

    globalProperties.$eel
      .reset_borders()()
      .then((response) => {
        if (response) {
          debugImageUrl.value = DEBUG_IMAGE_PATH;
        } else {
          state.showError(
            `Error creating preview image${
              settings.useWindowCapture ? ', make sure the window is not minimized' : ''
            }.`
          );
        }
      })
      .catch(() => {
        state.showError(
          `Error creating preview image${
            settings.useWindowCapture ? ', make sure the window is not minimized' : ''
          }.`
        );
      });
  }

  const useWindowCapture = computed({
    get() {
      return settings.useWindowCapture;
    },
    set(value) {
      showImage.value = true;
      scrollToTitle();
      debugImageUrl.value = '';

      globalProperties.$eel
        .write_settings_to_file({
          ...settings.$state,
          useWindowCapture: value,
        })()
        .then((success) => {
          settings.setUseWindowCapture(value);
          if (success) {
            debugImageUrl.value = DEBUG_IMAGE_PATH;
          } else {
            state.showError(
              `Error creating preview image ${
                settings.useWindowCapture ? ', make sure the window is not minimized' : ''
              }.`
            );
          }
        })
        .catch(() => {
          state.showError('Error updating settings.');
        });
    },
  });

  loadVideoDevices();
  loadOpenWindows();
</script>

<template>
  <v-card flat id="card">
    <v-card-title> Video Input </v-card-title>
    <v-card-subtitle>
      <template v-if="settings.useWindowCapture">
        <p>
          For the best results when using a window capture, it's recommended to use an OBS Windowed
          or Fullscreen Projector of your capture card source.
        </p>
        <p>
          Note: Please make sure that you crop the window border and keep the correct aspect ratio.
        </p>
      </template>
      <template v-else>
        <p>Select your capture card as the input video device and test if it's setup properly.</p>
        <p>
          Note: Using OBS Virtual Camera is NOT recommended due to compatibility and image quality
          issues.
        </p>
      </template>
    </v-card-subtitle>
    <v-card-text class="mt-4">
      <v-row align="center">
        <v-col cols="12" md="6">
          <v-autocomplete
            v-if="settings.useWindowCapture"
            v-model="selectedWindowCapture"
            @click="loadOpenWindows"
            @update:model-value="setWindowCapture"
            label="Window Capture"
            :items="openWindowNames"
            hide-details
            class="clickable"></v-autocomplete>
          <v-autocomplete
            v-else
            v-model="selectedDevice"
            @click="loadVideoDevices"
            @update:model-value="setVideoDevice"
            label="Video Device"
            :items="videoDevices"
            item-value="index"
            item-title="device_name"
            hide-details
            return-object
            class="clickable"></v-autocomplete>
        </v-col>
        <div class="d-flex flex-wrap">
          <v-btn @click="resetBorders" class="clickable ml-4">Show preview image</v-btn>
          <v-btn @click="() => (useWindowCapture = !useWindowCapture)" class="clickable ml-6">
            {{ useWindowCapture ? 'Use video device' : 'Use window capture' }}
          </v-btn>
        </div>
      </v-row>
      <template v-if="showImage">
        <div v-if="useWindowCapture" class="mt-8 d-flex justify-center">
          <v-text-field
            v-model="cropTop"
            label="Crop Top"
            type="number"
            min="0"
            density="compact"
            hide-details
            class="number-input clickable"></v-text-field>
        </div>
        <div class="d-flex align-center">
          <v-text-field
            v-if="useWindowCapture"
            v-model="cropLeft"
            label="Crop Left"
            type="number"
            min="0"
            density="compact"
            hide-details
            class="number-input clickable mr-4"></v-text-field>
        <v-img v-if="showImage" :src="debugImageUrl" aspect-ratio="1.7778" class="border mt-4">
          <template v-slot:placeholder>
            <div class="d-flex align-center justify-center fill-height">
              <v-progress-circular color="grey-lighten-4" indeterminate></v-progress-circular>
            </div> </template
        ></v-img>
          <v-text-field
            v-if="useWindowCapture"
            v-model="cropRight"
            label="Crop Right"
            type="number"
            min="0"
            density="compact"
            hide-details
            class="number-input clickable ml-4"></v-text-field>
        </div>
        <div v-if="useWindowCapture" class="d-flex mt-4 justify-center">
          <v-text-field
            v-model="cropBottom"
            label="Crop Bottom"
            type="number"
            min="0"
            density="compact"
            hide-details
            class="number-input clickable"></v-text-field>
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .number-input {
    max-width: 100px;
  }
</style>
