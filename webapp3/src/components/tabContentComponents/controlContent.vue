<template>
  <!-- Grid managing tab content -->
  <div uk-grid class="uk-height-1-1 uk-margin-remove uk-padding-remove">
    <div class="control-component">
      <paneControl />
    </div>
    <div class="view-component uk-width-expand">
      <miniStreamDisplay />
    </div>
  </div>
</template>

<script>
import paneControl from "./controlComponents/paneControl.vue";
// import streamDisplay from "./streamContent.vue";
import miniStreamDisplay from "../genericComponents/miniStreamDisplay.vue";

export default {
  name: "ControlContent",

  components: {
    paneControl,
    miniStreamDisplay,
  },
};
</script>

<style scoped>
.control-component {
  width: 605px;
}
</style>
