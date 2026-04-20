<template>
  <div id="app" class="uk-height-1-1 uk-margin-remove uk-padding-remove" :class="handleTheme">
    <loadingContent v-if="!ready" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue';

import loadingContent from "./components/loadingContent.vue";

const ready = false;

const handleTheme = computed(() => {
  return {
    "uk-light": true,
    "uk-background-secondary": true,
  }
})
</script>

<style scoped>
@import "../node_modules/uikit/src/less/uikit.less";
@import "./assets/less/theme.less";

.titlebar,
.titlebar > * {
  z-index: 1000 !important;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  height: 100%;
}

body,
html {
  height: 100%;
  overflow: hidden;
}

.uk-disabled {
  pointer-events: none;
  opacity: 0.4;
}

.control-component {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  width: 300px;
  height: 100%;
  padding: 0;
  background-color: rgba(180, 180, 180, 0.03);
  border-width: 0 1px 0 0;
  border-style: solid;
  border-color: rgba(180, 180, 180, 0.25);
}

.view-component {
  overflow-y: auto;
  overflow-x: hidden;
  height: 100%;
  padding: 0;
}

.image-fit {
  height: 80%;
  width: 100%;
  object-fit: contain;
  overflow-y: clip;
}

.section-content {
  padding: 0;
  height: 100%;
}

.thumbnail-fit {
  max-height: 120px;
  max-width: 240px;
  object-fit: contain;
  overflow-y: hidden;
}
</style>
