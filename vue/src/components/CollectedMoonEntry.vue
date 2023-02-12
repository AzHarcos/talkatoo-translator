<script setup>
    import { computed } from "vue";
    import { storeToRefs } from "pinia"
    import { useStore } from "../store";
    import { moonToString } from "../composables";

    const props = defineProps({
        moon: Object
    })

    const store = useStore();
    const { mentionedMoons } = storeToRefs(store);

    const isMoonUnmentioned = computed(() => {
      return !moon.is_story && !mentionedMoons.some(possibleMoons => possibleMoons.some(m => moonsAreEqual(moon, m)));
    });

    const moonString = computed(() => {
        return moonToString(moon);
    });
</script>

<template>
    <div v-if="isMoonUnmentioned" class="list-item-content">
        <span>{{ moonString }}</span>
        <span class="material-symbols-outlined">close</span>
    </div>
    <span v-else @click="store.setMoonUncollected(moon)">{{ moonString }}</span>
</template>