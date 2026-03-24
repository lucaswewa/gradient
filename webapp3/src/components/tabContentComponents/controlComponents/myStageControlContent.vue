<template>
  <div>
    <ul>
      <propertyControl
        thing-name="stage"
        property-name="position"
        label="position (mm)"
        :read-back="true"
        :read-back-delay="200"
      />
      <actionButton
        thing="stage"
        action="move_rel"
        poll-interval="100"
        :submit-data="{delta: 0.5, block_cancellation: false}"
        submit-label="move rel"
      />
      <actionButton
        thing="stage"
        action="move_abs"
        poll-interval="100"
        :submit-data="{position: 12, block_cancellation: false}"
        submit-label="move abs"
      />
      <li>Dpad Control: XY Z</li>
      <li>Step Size</li>
      <li>Positions</li>
      <li>Speeds</li>
      <li>Accelerations</li>
      <li>Limits</li>
      <li>Homing</li>
      <li>Jogging</li>
      <li>Set Origin</li>
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
