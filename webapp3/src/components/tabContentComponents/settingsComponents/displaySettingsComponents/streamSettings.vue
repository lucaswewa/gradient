<template>
  <div id="streamSettings" class="uk-width-large">
    <div>
      <h3>Stream Settings</h3>
      <label
        ><input v-model="disableStream" class="uk-checkbox" type="checkbox" /> Disable Web
        Stream</label
      >
      <p class="uk-margin-small">This will disable the embedded web stream of the camera.</p>
    </div>
  </div>
</template>

<script>
import { useStore } from "@/store";

// Export main app
export default {
  name: "StreamSettings",

  data: function () {
    return {
      store: () => useStore(),
    };
  },

  computed: {
    disableStream: {
      get() {
        return this.store().state.disableStream;
      },
      set(value) {
        this.store().changeDisableStream(value);
      },
    },
  },
};
</script>

<style lang="less"></style>
