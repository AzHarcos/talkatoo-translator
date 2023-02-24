<script setup>
  import { computed } from 'vue';
  import availableLanguages from '../../consts/availableLanguages';

  const props = defineProps({
    label: String,
    selected: String,
    pattern: String,
    loading: Boolean,
  });

  const emit = defineEmits(['input']);

  const filteredLanguages = props.pattern
    ? availableLanguages.filter((language) => language.label.includes(props.pattern))
    : availableLanguages;

  const selectedLanguage = computed(() => {
    return filteredLanguages.find((entry) => entry.id === props.selected)?.id ?? '';
  });

  function updateLanguage(language) {
    emit('input', language);
    document.activeElement.blur();
  }
</script>

<template>
  <v-autocomplete
    :model-value="selectedLanguage"
    @update:modelValue="updateLanguage"
    :label="label"
    :items="filteredLanguages"
    :loading="loading"
    item-value="id"
    item-title="label"
    hide-details
    class="clickable"></v-autocomplete>
</template>
