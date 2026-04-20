<template>
  <div class="uk-flex uk-flex-column uk-flex-center uk-height-1-1">
    <div v-if="waiting" class="uk-align-center" uk-spinner="ratio: 3"></div>
    <div v-if="waiting" class="uk-align-center">Loading...</div>
    <span class="material-symbols-outlined uk-align-center error-icon">error_outline</span>
    <div v-if="error" class="uk-align-center">
      {{ error }}
    </div>
    <div class="uk-align-center">
      <devTools class="uk-width-medium"></devTools>
    </div>
  </div>
</template>

<script setup lang="ts">
import devTools from "./tabContentComponents/aboutComponents/devTools.vue";

const waiting = true;
const error = 'cannot connect to the server'
</script>

<style scoped lang="less">
.error-icon {
  font-size: 120px;
}
</style>
