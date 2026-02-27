<template>
  <div id="cameraSettings" ref="cameraSettingsContainer"
       class="uk-width-large">
    <div class="uk-width-large">
      <h3>Automatic calibration</h3>
      <!-- <cameraCalibrationSettings :camera-uri="cameraUri" /> -->
      <h3>Manual camera settings</h3>
      <div class="uk-margin-small-bottom">
        <server-specified-property-control
          v-for="(setting, index) in manualCameraSettings"
          :key="'cam_setting' + index"
          :property-data="setting"
        />
      </div>
    </div>
  </div>
</template>

<script>
// import cameraCalibrationSettings from "./cameraSettingsComponents/cameraCalibrationSettings.vue";
import ServerSpecifiedPropertyControl from "../../labThingsComponents/serverSpecifiedPropertyControl.vue";

import { useStore } from "@/store";
import useLTI from "@/mixins/labThingsMixins";
const lti = useLTI();

// Export main app
export default {
  name: "myCameraSettings",

  components: {
    // cameraCalibrationSettings,
    ServerSpecifiedPropertyControl,
  },

  data() {
    return {
      manualCameraSettings: [],
      store: () => useStore(),
    };
  },

  computed: {
    cameraUri: function () {
      return `${this.store().baseUri}/camera/`;
    },
  },

  async created() {
    this.manualCameraSettings = await lti.readThingProperty("camera", "manual_camera_settings");
  },
};
</script>

<style lang="less">
</style>
