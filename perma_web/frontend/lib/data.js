import { reactive, toRefs } from "vue";
import { defaultError } from './errors'
import { validStates, transitionalStates } from '../lib/consts.js'
import { getErrorFromNestedObject } from '../lib/errors';

export const useFetch = async (baseUrl, options) => {
  const state = reactive({
    isLoading: false,
    hasError: false,
    errorMessage: '',
    data: null
  })

  const url = options ? `${baseUrl}?${new URLSearchParams(options)}` : baseUrl

  const fetchData = async () => {
    state.isLoading = true;

    try {
      const response = await fetch(url); 
      if (!response?.ok) {
        throw new Error(response.statusText) 
      }

      state.data = await response.json()

    } catch (err) {
      state.hasError = true
      state.errorMessage = err?.message.length ? err.message : defaultError
    }
    state.isLoading = false
  }
  await fetchData()
  return {
    ...toRefs(state)
  }
}

export const useBatchDetailsFetch = async (batchCaptureId) => {
  const { data, hasError, errorMessage } = await useFetch(`/api/v1/archives/batches/${batchCaptureId}`)

  if (hasError.value || !data.value.capture_jobs) {
      console.log(errorMessage.value)
      return
  }

  const { allJobs, progressSummary } = useFormatBatchDetails(data.value.capture_jobs)

  return {
    allJobs, progressSummary
  }
}

export const useFormatBatchDetails = ((captureJobs) => {
  const steps = 6
  const allJobs = captureJobs.reduce((accumulatedJobs, currentJob) => {
      const includesError = !validStates.includes(currentJob.status)
      const isCapturing = transitionalStates.includes(currentJob.status)

      let jobDetail = {
          ...currentJob,
          message: includesError ? getErrorFromNestedObject(JSON.parse(currentJob.message)) : '',
          progress: (currentJob.step_count / steps) * 100,
          url: `${window.location.hostname}/${currentJob.guid}`
      };

      if (isCapturing) {
          accumulatedJobs.completed = false;
      }

      if (includesError) {
          accumulatedJobs.errors += 1;
      }

      return {
          ...accumulatedJobs,
          details: [...accumulatedJobs.details, jobDetail]
      };
  }, {
      details: [],
      completed: true,
      errors: 0
  });

  const totalProgress = allJobs.details.reduce((total, job) => total + job.progress, 0);
  const maxProgress = allJobs.details.length * 100;
  const percentComplete = Math.round((totalProgress / maxProgress) * 100);

  const progressSummary = allJobs.completed ? "Batch complete." : `Batch ${percentComplete}% complete.`;

  return { allJobs, progressSummary }
})