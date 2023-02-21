<script setup>
  import { ref, nextTick } from 'vue';
  import { useDisplay } from 'vuetify';

  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';
  import { scrollToBottom } from '@/composables';

  const { lgAndUp } = useDisplay();

  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();

  const videoDevices = ref([]);
  const selectedDevice = ref(settings.videoDevice);
  const showImage = ref(false);
  const DEBUG_IMAGE_URL = 'http://localhost:8083/assets/border_reset_img.png';
  const debugImageUrl = ref(DEBUG_IMAGE_URL);

  globalProperties.$eel
    .get_video_devices()()
    .then((response) => {
      if (response) {
        videoDevices.value = response;
      } else {
        console.log('empty video devices');
      }
    })
    .catch(() => console.log('error getting video devices'));

  function setVideoDevice(device) {
    if (!showImage.value) {
      showImage.value = true;
      setTimeout(() => (debugImageUrl.value = ''), 100);
      setTimeout(scrollToBottom, 400);
    } else {
      scrollToBottom();
      debugImageUrl.value = '';
    }

    globalProperties.$eel
      .set_video_index(device.index)()
      .then((response) => {
        if (response) {
          settings.setVideoDevice(device);
          debugImageUrl.value = DEBUG_IMAGE_URL;
        } else {
          selectedDevice.value = settings.videoDevice;
          console.log('error setting video device');
          document.activeElement.blur();
        }
      })
      .catch(() => {
        selectedDevice.value = settings.videoDevice;
        console.log('error setting video device');
        document.activeElement.blur();
      });
  }

  function resetBorders() {
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
          debugImageUrl.value = DEBUG_IMAGE_URL;
        } else {
          console.log('error resetting borders');
        }
      })
      .catch((err) => {
        console.log(err);
        console.log('error resetting borders');
      });
  }
</script>

<template>
  <v-card flat>
    <v-card-title> Image recognition settings </v-card-title>
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
