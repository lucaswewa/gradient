<template>
  <div class="host-input">
    <div v-if="store().state.available">
      <div>
        <div class="uk-margin-small-bottom">
          <b>Thing:</b>
          <br />
          TesterThing
        </div>
        <div class="uk-margin-small-bottom">
          <b>API Origin:</b>
          <br />
          {{ store().state.origin }}
        <hr />
        </div>
        <property-control
          thing-name="tester"
          property-name="speed"
          label="Speed:"
          step="0.1"
          :read-back="true"
          :read-back-delay="400"
        />
        <property-control
          thing-name="tester"
          property-name="moving"
          label="Is Moving:"
          :read-back="true"
          :read-back-delay="400"
        />
        <property-control
          thing-name="tester"
          property-name="position"
          label="Position [x, y, z]:"
          :read-back="true"
          :read-back-delay="400"
        />
      </div>
      <hr />
    </div>
    <div v-else-if="store().state.waiting">Loading...</div>
    <div v-else-if="store().state.error"><b>Error:</b> {{ store().state.error }}</div>
    <div v-else>No active connection</div>
  </div>
</template>

<script>
import propertyControl from "@/components/labThingsComponents/propertyControl.vue";
import { useStore } from "../../../store.js";
import useLTI from "@/mixins/labThingsMixins";

const lti = useLTI();

export default {
  name: "PropertyPane",
  components: {
    propertyControl
  },

  data: function () {
    return {
      version: undefined,
      version_source: undefined,
      store: () => useStore(),
    };
  },

  computed: {
    cameraType() {
      // No need to check as the microscope won't start up without a camera defined
      return lti.thingDescription("camera").title;
    },
    stageType() {
      return lti.thingAvailable("stage") ? lti.thingDescription("stage").title : undefined;
    },
    illuminationType() {
      return lti.thingAvailable("illumination")
        ? lti.thingDescription("illumination").title
        : undefined;
    },
  },

  async mounted() {
    let version_data = await lti.readThingProperty("system", "version_data");
    this.version = version_data.version;
    this.version_source = this.truncate(version_data.version_source);
  },

  methods: {
    truncate(string, max_length = 15) {
      if (!(typeof string === "string" || string instanceof String)) {
        return string;
      }
      if (string.length <= max_length) {
        return string;
      }
      return string.slice(0, max_length - 3) + "...";
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less"></style>
