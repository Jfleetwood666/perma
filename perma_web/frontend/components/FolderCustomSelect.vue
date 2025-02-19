<script setup>
import { computed, ref, nextTick } from 'vue'
import { globalStore } from '../stores/globalStore'
import { onClickOutside } from '@vueuse/core'

const props = defineProps({
    folders: Array,
    personalFolderId: Number,
    selectLabel: String,
})

const selectContainerRef = ref(null)
const selectButtonRef = ref(null)
const selectListRef = ref(null)
const isSelectExpanded = ref(false)
const selectedOption = computed(() => !!globalStore.selectedFolder.folderId ? globalStore.selectedFolder.path.join(" > ") : 'Please select a folder')

const getFolderHeader = (folder) => {
    if (folder.registrar) {
        return folder.registrar
    }

    else if (folder.sponsored_by) {
        return "Sponsored Links"
    }

    return "Personal Links"
}

const showLinksRemaining = computed(() => globalStore.selectedFolder.folderId === props.personalFolderId || !!globalStore.selectedFolder.isReadOnly)
const linksRemaining = computed(() => {
    if (globalStore.selectedFolder.isReadOnly) {
        return 0
    }

    else if (globalStore.linksRemaining === Infinity) {
        return "unlimited"
    }

    return globalStore.linksRemaining
})

// Select Event Handlers
onClickOutside(selectContainerRef, () => {
    if (!isSelectExpanded) { return }
    isSelectExpanded.value = false
})

const handleSelectToggle = () => {
    isSelectExpanded.value = !isSelectExpanded.value
}

const handleKeyboardSelectToggle = async (e) => {
    const isButton = e.target.matches('button')

    if (!isButton) {
        return
    }

    if (isSelectExpanded.value) {
        return handleArrowDown(e)
    }

    handleSelectToggle()
    await nextTick()
}

const handleFocus = (index) => {
    const itemToFocus = selectListRef.value.querySelector(`[data-index="${index}"]`);
    itemToFocus.focus();
};

const handleArrowDown = (e) => {
    const currentIndex = parseInt(e.srcElement.dataset?.index)

    if (!currentIndex) {
        handleFocus(0)
    }

    if (currentIndex < props.folders.length) {
        handleFocus(currentIndex + 1)
    }
}

const handleArrowUp = (e) => {
    const currentIndex = parseInt(e.srcElement.dataset.index)
    if (currentIndex > 0) {
        handleFocus(currentIndex - 1)
    }
}

const handleClose = () => {
    isSelectExpanded.value = false
    selectButtonRef.value.focus()
}

const handleSelection = (e) => {
    const isSpan = e.target.matches('span')
    const target = isSpan ? e.target.parentElement : e.target

    const { orgid: orgId, folderid: folderId } = target.dataset

    if (!folderId) {
        return handleClose()
    }

    // Call a custom event that triggers triggerOnWindow function
    const updateSelections = new CustomEvent("dropdown.selectionChange", { detail: { data: { folderId: JSON.parse(folderId), orgId: orgId ? parseInt(orgId) : null } } });
    window.dispatchEvent(updateSelections);

    handleClose()
}


</script>


<template>
    <div id="organization_select_form">
        <span class="label-affil">{{ props.selectLabel }}</span>
        <div ref="selectContainerRef" @keydown.home.prevent="handleFocus(0)"
            @keydown.end.prevent="handleFocus(props.folders.length)" @keydown.esc="handleClose"
            @keydown.tab="handleClose" class="dropdown dropdown-affil" :class="{ 'open': isSelectExpanded }">
            <button ref="selectButtonRef" @keydown.down.prevent.self="handleKeyboardSelectToggle"
                @keydown.enter.prevent.self="handleKeyboardSelectToggle"
                @keydown.space.prevent="handleKeyboardSelectToggle" @click="handleSelectToggle"
                class="dropdown-toggle selector selector-affil needsclick" type="button" aria-haspopup="listbox"
                :aria-expanded="isSelectExpanded" aria-owns="folder-select-list">
                {{ selectedOption }}
                <span v-if="globalStore.selectedFolder.isPrivate" class="ui-private"></span>
                <span v-if="showLinksRemaining" class="links-remaining">
                    {{ linksRemaining }}
                </span>
            </button>
            <ul ref="selectListRef" v-if="isSelectExpanded" @keydown.down="handleArrowDown" @keydown.up="handleArrowUp"
                @click.propagate="handleSelection" @keydown.space="handleSelection"
                @keydown.enter.prevent="handleSelection" role="listbox" aria-label="Folder options"
                class="dropdown-menu selector-menu" :class="{ 'open': isSelectExpanded }">
                <template v-for="( folder, index ) in  props.folders ">
                    <li v-if="folder.registrar !== props.folders[index - 1]?.registrar" role="presentation"
                        class="dropdown-header" :class="{ 'sponsored': folder.sponsored_by }">
                        {{ getFolderHeader(folder) }}
                    </li>
                    <li tabindex="-1" class="dropdown-item" role="option"
                        :aria-selected="globalStore.selectedFolder.orgId === folder.id || globalStore.selectedFolder.path[1] === folder.name"
                        :data-index="index" :data-orgid="folder.sponsored_by ? null : folder.id"
                        :data-folderid="folder.sponsored_by ? `[${folder.parent},${folder.id}]` : folder.shared_folder.id">
                        {{ folder.name }}
                        <span v-if="folder?.default_to_private"
                            class="dropdown-item-supplement ui-private">(Private)</span>
                        <span v-if="folder.read_only" class="dropdown-item-supplement links-remaining">0</span>
                        <span v-else class='dropdown-item-supplement links-unlimited'
                            :class="{ 'sponsored': folder.sponsored_by }">unlimited</span>
                    </li>
                </template>
                <li class="dropdown-header personal" role="presentation" aria-hidden="true">Personal Links</li>
                <li tabindex="-1" class="dropdown-item personal-links" role="option"
                    :aria-selected="globalStore.selectedFolder.folderId === props.personalFolderId"
                    :data-index="props.folders.length" :data-folderid="props.personalFolderId">Personal Links <span
                        class="dropdown-item-supplement links-remaining">{{
            globalStore.linksRemaining ===
                Infinity ?
                'unlimited' :
                        globalStore.linksRemaining }}</span>
                </li>
            </ul>
        </div>
    </div>
</template>