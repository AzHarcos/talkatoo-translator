<script setup>
  import { ref, computed } from 'vue';

  const emit = defineEmits(['confirm', 'close']);

  const skipResetConfirmation = ref(false);

  const showDialog = computed({
    get() {
      return true;
    },
    set(value) {
      if (!value) {
        close();
      }
    },
  });

  function confirm() {
    emit('confirm', skipResetConfirmation.value);
  }

  function close() {
    emit('close');
  }
</script>

<template>
  <v-dialog v-model="showDialog" width="400">
    <v-card class="dialog">
      <v-card-title class="pt-4 d-flex justify-space-between">
        <div class="text-h6">Resetting the run</div>
        <v-icon @click="close" size="1em" class="close-icon clickable">mdi-close</v-icon>
      </v-card-title>
      <v-card-text class="pl-4 pt-2 pb-2 text-body-1">
        <p>Do you really want to reset the run?</p>
      </v-card-text>
      <v-card-actions class="pa-2 pr-4 pt-0 d-flex justify-space-between">
        <v-checkbox
          v-model="skipResetConfirmation"
          label="Don't ask again"
          color="primary"
          class="clickable"
          hide-details></v-checkbox>
        <v-btn class="clickable ml-auto" variant="outlined" @click="confirm">Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped></style>
