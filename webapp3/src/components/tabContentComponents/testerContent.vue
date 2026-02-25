<template>
  <!-- Grid managing tab content -->
  <div class="uk-height-1-1 view-component">
    <div class="uk-padding-small">
      <propertyPane class="uk-width-large" />
      <actionPane class="uk-width-large" />
    </div>
  </div>
</template>

<script>
import propertyPane from "./testerComponents/propertyPane.vue";
import actionPane from "./testerComponents/actionPane.vue";

export default {
  name: "TesterContent",

  components: {
    propertyPane,
    actionPane,
  },
};
</script>
