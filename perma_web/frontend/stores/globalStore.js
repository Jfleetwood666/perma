import { reactive } from 'vue'

export const globalStore = reactive({
  captureStatus: 'ready',
  updateCapture(state) {
    this.captureStatus = state
  },

  captureErrorMessage: '',
  updateCaptureErrorMessage(message) {
    this.captureErrorMessage = message
  },

  fetchErrorMessage: '',
  updateFetchErrorMessage(message) {
    this.fetchErrorMessage = message
  },

  linksRemaining: '',
  updateLinksRemaining(links) {
    this.linksRemaining = links
  },

  linksRemainingStatus: '',
  updateLinksRemainingStatus(status) {
    this.linksRemainingStatus = status
  },

  userTypes: [],
  updateUserTypes(types) {
    this.userTypes = types
  },

  selectedFolder: {
    path: [],
    id: [], 
    orgId: '',
    sponsorId: '',
    isPrivate: false,
    isReadOnly: false,
    isOutOfLinks: false,
  },

  updateFolderSelection(selection) {
    this.selectedFolder = selection
  },

  organizationFolders: [],
  updateOrganizationFolders(orgFolders) {
    this.organizationFolders = orgFolders
  },

  organizationFoldersById: {},
  updateOrganizationFoldersById(orgFoldersById) {
    this.organizationFoldersById = orgFoldersById
  }, 

  sponsoredFolders: [], 
  updateSponsoredFolders(sponsoredFolders) {
    this.sponsoredFolders = sponsoredFolders
  }
})