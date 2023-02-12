<script setup>
    import { computed } from "vue";
    import PendingMoonList from './PendingMoonList.vue'
    import CollectedMoonList from './CollectedMoonList.vue';
    import { useStore } from '../store';
    import { areMoonsPending } from '../composables';

    const store = useStore();

    const selectedKingdomPendingMoons = computed(() => {
      return store.mentionedMoons.filter(areMoonsPending);
    });

    const selectedKingdomCollectedMoons = computed(() => {
        return store.collectedMoons.filter(moon => moon.kingdom === store.selectedKingdom);
    });
</script>

<template>
    <div v-if="selectedKingdomPendingMoons.length > 0 || selectedKingdomCollectedMoons.length > 0" class="container">
        <div class="card">
            <div class="list-container">
                <PendingMoonList v-if="selectedKingdomPendingMoons.length > 0" :moons="selectedKingdomPendingMoons"/>
                <CollectedMoonList v-if="selectedKingdomCollectedMoons.length > 0" :moons="selectedKingdomCollectedMoons"/>
            </div>
        </div>
    </div>
</template>