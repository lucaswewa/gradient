<template>
  <div>
    <myAppSettings />
    <myStreamSettings />
  </div>
</template>

<script>
import myAppSettings from "./displaySettingsComponents/myAppSettings.vue";
import myStreamSettings from "./displaySettingsComponents/myStreamSettings.vue";

// Export main app
export default {
  name: "myDisplaySettings",

  components: {
    myStreamSettings,
    myAppSettings,
  },
};
</script>
