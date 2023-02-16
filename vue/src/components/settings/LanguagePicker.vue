<script setup>
  import { ref } from 'vue';

  const props = defineProps({
    modelValue: String,
    label: String,
    preselected: String,
    pattern: String,
  });

  defineEmits(['update:modelValue']);

  const availableLanguages = [
    {
      id: 'english',
      label: 'English',
    },
    {
      id: 'chinese_simplified',
      label: 'Simplified Chinese',
    },
    {
      id: 'chinese_traditional',
      label: 'Traditional Chinese',
    },
    {
      id: 'dutch',
      label: 'Dutch',
    },
    {
      id: 'french_france',
      label: 'French',
    },
    {
      id: 'french_canada',
      label: 'French (Canadian)',
    },
    {
      id: 'german',
      label: 'German',
    },
    {
      id: 'italian',
      label: 'Italian',
    },
    {
      id: 'japanese',
      label: 'Japanese',
    },
    {
      id: 'korean',
      label: 'Korean',
    },
    {
      id: 'russian',
      label: 'Russian',
    },
    {
      id: 'spanish_spain',
      label: 'Spanish',
    },
    {
      id: 'spanish_latin_america',
      label: 'Spanish (Latin America)',
    },
  ];

  const preselectedLanguage =
    availableLanguages.find((entry) => entry.id === props.preselected)?.id ?? '';

  const selectedLanguage = ref(preselectedLanguage);
  const requiredRules = [() => 'Language is required'];

  function filterByPattern(item) {
    return props.pattern && item.includes(pattern);
  }
</script>

<template>
  <v-autocomplete
    v-model="selectedLanguage"
    @input="$emit('update:modelValue', $event.target.value)"
    :label="label"
    :items="availableLanguages"
    :filter="filterByPattern"
    item-value="id"
    item-title="label"
    :rules="requiredRules"
    required></v-autocomplete>
</template>
p
