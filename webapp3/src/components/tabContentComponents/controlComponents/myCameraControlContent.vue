<template>
  <div>
    <ul>
      <propertyControl
        thing-name="camera"
        property-name="exposure"
        label="Exposure time (us)"
      />
      <propertyControl
        thing-name="camera"
        property-name="gain"
        label="Gain (dB)"
      />
      <actionButton
        thing="camera"
        action="set_shutter"
        :submit-data="{shutter_on: true}"
        submit-label="Open shutter"
      />
      <actionButton
        thing="camera"
        action="set_shutter"
        :submit-data="{shutter_on: false}"
        submit-label="Close shutter"
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

