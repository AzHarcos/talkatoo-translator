<script setup>
  import { ref } from 'vue';
  import availableLanguages from '../../consts/availableLanguages';

  const props = defineProps({
    label: String,
    preselected: String,
    pattern: String,
  });

  const emit = defineEmits(['input']);

  const filteredLanguages = props.pattern
    ? availableLanguages.filter((language) => language.label.includes(props.pattern))
    : availableLanguages;

  const preselectedLanguage =
    availableLanguages.find((entry) => entry.id === props.preselected)?.id ?? '';

  const selectedLanguage = ref(preselectedLanguage);
</script>

<template>
  <v-autocomplete
    v-model="selectedLanguage"
    @update:modelValue="(event) => $emit('input', event)"
    :label="label"
    :items="filteredLanguages"
    item-value="id"
    item-title="label"
    hide-details></v-autocomplete>
</template>
