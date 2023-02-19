<script setup>
  import { useSettings } from '@/stores/settings';
  import useCurrentInstance from '@/hooks/useCurrentInstance';

  const settings = useSettings();
  const { globalProperties } = useCurrentInstance();
</script>

<template>
  <v-card flat>
    <v-card-title> Image recognition settings </v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" sm="6">
          <v-text-field label="Video index"></v-text-field>
        </v-col>
        <v-col cols="12" sm="6">
          <v-btn>Reset capture border</v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
