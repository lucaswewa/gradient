<template>
  <!-- Grid managing tab content -->
  <div uk-grid class="uk-height-1-1 uk-margin-remove uk-padding-remove">
    <div class="control-component">
      <offsetControl />
    </div>
    <div class="view-component uk-width-expand">
      <offsetChart/>
    </div>
  </div>
</template>

<script>
import offsetControl from "./offsetComponents/offsetControl.vue";
import offsetChart from "./offsetComponents/offsetChart.vue";

export default {
  name: "ControlContent",

  components: {
    offsetControl,
    offsetChart,
  },
};
</script>

<style scoped>
.control-component {
  width: 605px;
}
</style>
