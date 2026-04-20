<template>
  <div class="uk-flex uk-flex-column uk-flex-center uk-height-1-1">
    <div v-if="store.state.waiting" class="uk-align-center" uk-spinner="ratio: 3"></div>
    <div v-if="store.state.waiting" class="uk-align-center">Loading...</div>
    <span class="material-symbols-outlined uk-align-center error-icon">error_outline</span>
    <div v-if="store.state.error" class="uk-align-center">
      {{ store.state.error }}
    </div>
    <div class="uk-align-center">
      <devTools class="uk-width-medium"></devTools>
    </div>
  </div>
</template>

<script setup lang="ts">
import devTools from "./tabContentComponents/aboutComponents/devTools.vue";
import store from "@/store.ts"
</script>

<style scoped lang="less">
.error-icon {
  font-size: 120px;
}
</style>
