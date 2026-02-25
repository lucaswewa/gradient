import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'

function getOriginFromLocation() {
  // This will default to the same origin that's serving
  // the web app - but can be overridden by the URL.
  // See also devTools.vue which can change the origin.
  let url = new URL(window.location.href);
  let origin = url.searchParams.get("overrideOrigin");
  if (origin) {
    return origin;
  } else {
    return url.origin;
  }
}

export const useStore = defineStore('store', () => {
  const state = reactive({
    origin: getOriginFromLocation(),
    available: false,
    waiting: false,
    error: "",
    autoGpuPreview: false,
    trackWindow: true,
    activeStreams: {},
    microscopoeHostname: "",
    appTheme: "system",
    disableStream: false,
    overrideOrigin: "http://localhost:5000",
    navigationStepSize: {
      x: 200,
      y: 200,
      z: 50,
    },
    navigationInvert: {
      x: false,
      y: false,
      z: false,
    }
  })

  function changeOrigin(origin) {
    state.origin = origin
  }
  function changeWaiting(waiting) {
    state.waiting = waiting
  }

  function changeDisableStream(disabled) {
    state.disableStream = disabled;
  }
  function changeAutoGpuPreview(enabled) {
    state.autoGpuPreview = enabled;
  }
  function changeTrackWindow(enabled) {
    state.trackWindow = enabled;
  }
  function changeAppTheme(theme) {
    state.appTheme = theme;
  }
  function resetState() {
    state.waiting = false;
    state.available = false;
    state.error = null;
  }
  function setConnected() {
    state.waiting = false;
    state.available = true;
  }
  function setErrorMessage(msg) {
    state.error = msg;
  }
  function addStream(id) {
    state.activeStreams[id] = true;
  }
  function removeStream(id) {
    state.activeStreams[id] = false;
  }
  function changeMicroscopeHostname(value) {
    state.microscopeHostname = value;
  }
  function changeOverrideOrigin(value) {
    state.overrideOrigin = value;
  }
  function changeNavigationStepSize(value) {
    state.navigationStepSize = value;
  }
  function changeNavigationInvert(value) {
    state.navigationInvert = value;
  }

  const baseUri = computed(() => {
    return state.origin
  })

  const ready = computed(() => {
    return state.available
  })

  function set_available(available) {
    state.available = available
  }

  return {
    state,
    changeOrigin,
    changeWaiting,
    changeDisableStream,
    changeAutoGpuPreview,
    changeTrackWindow,
    changeAppTheme,
    resetState,
    setConnected,
    setErrorMessage,
    addStream,
    removeStream,
    changeMicroscopeHostname,
    changeOverrideOrigin,
    changeNavigationStepSize,
    changeNavigationInvert,
    set_available,
    baseUri,
    ready
  }
})
