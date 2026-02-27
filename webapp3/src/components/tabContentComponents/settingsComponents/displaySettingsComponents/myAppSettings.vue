<template>
  <div id="myAppSettings" class="uk-width-medium">
  <h3>Appearance</h3>
  <p>
    <label>
      Theme
      <select v-model="appTheme" class="uk-select">
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="system">System</option>
      </select>
    </label>
  </p>
    <p>
      <button class="uk-button uk-button-default" @click="toggleFullscreen">
        Toggle Fullscreen
      </button>
    </p>
</div>
</template>

<script>
import { useStore } from '@/store';

// Export main app
export default {
  name: "myAppSettings",

  data: function () {
    return {
      store: () => useStore(),
    };
  },

  computed: {
    appTheme: {
      get() {
        return this.store().state.appTheme;
      },
      set(value) {
        this.store().changeAppTheme(value);
      },
    },
  },

  methods: {
    async toggleFullscreen() {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    },
  },
};
</script>

<style lang="less"></style>
