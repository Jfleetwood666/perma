<script setup>
import { ref } from 'vue'
import { useBatchHistoryFetch } from '../lib/data'

const linkRecords = ref([]) 
const handleLinkBatchHistoryFetch = async () => {
    const { linkBatches } = await useBatchHistoryFetch();
    linkRecords.value = linkBatches.value
};
</script>

<template>
    <!-- For Testing Only -->
    <button :onClick="handleLinkBatchHistoryFetch">
        Fetch Batch History
    </button>
    <ul v-if="linkRecords.length" v-for="link in linkRecords">
        <li>
            {{ link.started_on }}
        </li>
    </ul>
</template>