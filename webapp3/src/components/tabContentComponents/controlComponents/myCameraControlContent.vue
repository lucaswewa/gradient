<template>
  <div>
    <ul>
      <propertyControl
        thing-name="camera"
        property-name="exposure_time"
        label="Exposure time (us)"
        :read-back="true"
        :read-back-delay="400"
      />
      <propertyControl
        thing-name="camera"
        property-name="gain"
        label="Gain (dB)"
        :read-back="true"
        :read-back-delay="400"
      />
      <actionButton
        thing="camera"
        action="start_streaming"
        :submit-data="{}"
        submit-label="Start Streaming"
      />
      <actionButton
        thing="camera"
        action="stop_streaming"
        :submit-data="{}"
        submit-label="Stop Stream"
      />
      <actionButton
        thing="camera"
        action="arm"
        :submit-data="{}"
        submit-label="Arm"
      />
      <actionButton
        thing="camera"
        action="software_trigger"
        :submit-data="{}"
        submit-label="Software Trigger"
      />
      <actionButton
        thing="camera"
        action="disarm"
        :submit-data="{}"
        submit-label="Disarm"
      />
      <!-- <li>Pixel Format Settings</li>
      <li>Region of Interest (ROI) Settings</li>
      <li>Objective Controls</li> -->
    </ul>
  </div>
</template>

<script>
import propertyControl from '@/components/labThingsComponents/propertyControl.vue';
import actionButton from '@/components/labThingsComponents/actionButton.vue';

export default {
  name: "projectorControl",

  components: {
    propertyControl,
    actionButton,
  },

  data: function() {
    return {
      projectors: [
        {name: "projector_r", label: "Projector Red"},
        {name: "projector_g", label: "Projector Grn"},
        {name: "projector_b", label: "Projector Blu"},
      ]
    }
  }
}
</script>

<style lang="less" scoped>
</style>

