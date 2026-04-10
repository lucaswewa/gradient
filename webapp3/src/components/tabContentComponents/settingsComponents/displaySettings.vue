<template>
  <div id="displaysettings">
    <div class="uk-grid uk-grid-divider uk-child-width-expand" uk-grid>
      <div class="uk-width-large">
        <appSettings />
        <streamSettings />
      </div>
      <div id="mini-stream">
        <miniStreamDisplay />
      </div>
    </div>
  </div>
</template>

<script>
import appSettings from "./displaySettingsComponents/appSettings.vue";
import streamSettings from "./displaySettingsComponents/streamSettings.vue";
import miniStreamDisplay from "../../genericComponents/miniStreamDisplay.vue";

// Export main app
export default {
  name: "DisplaySettings",

  components: {
    streamSettings,
    appSettings,
    miniStreamDisplay,
  },
};
</script>
