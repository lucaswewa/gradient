<template>
  <div class="host-input">
    <div v-if="true">
      <div>
        <div class="uk-margin-small-bottom">
          <b>ActionButton no modal</b>
          <br />
        </div>
          <div id="asdf" class="uk-margin">
            <property-control
              thing-name="projector_r"
              property-name="led"
              label="Projector Red LED"
              :read-back="true"
              :read-back-delay="500"
            />
          </div>
          <div id="asdf" class="uk-margin">
            <property-control
              thing-name="projector_g"
              property-name="led"
              label="Projector Grn LED"
              :read-back="true"
              :read-back-delay="500"
            />
          </div>
          <div id="asdf" class="uk-margin">
            <property-control
              thing-name="projector_b"
              property-name="led"
              label="Projector Blu LED"
              :read-back="true"
              :read-back-delay="500"
            />
          </div>
          <div id="asdf" class="uk-margin">
            <property-control
              thing-name="stage"
              property-name="speed"
              label="Stage Speed"
              :read-back="true"
              :read-back-delay="500"
            />
          </div>
          <div id="asdf" class="uk-margin">
            <property-control
              thing-name="stage"
              property-name="speed"
              label="Stage speed"
              :read-back="true"
              :read-back-delay="500"
            />
          </div>
      </div>
    </div>
  </div>
</template>

<script>
import PropertyControl from "./propertyControl.vue";
import useLTI from "@/mixins/labThingsMixins";
const lti = useLTI();

export default {
  name: "PropertyControlTester",
  components: {
    PropertyControl,
  },

  data: function () {
    return {
      version: undefined,
      version_source: undefined,
    };
  },

  computed: {
  },

  async beforeMount() {
    await lti.thingDescriptions("http://localhost:5000/thing_descriptions")
  },

  async mounted() {
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
<style scoped>
#log-display {
  height: 20em;
}
.control-component {
  width: 33%;
}
.workflow-name {
  margin-bottom: 0.5rem;
}
.workflow-blurb {
  color: #a2a2a2;
}
</style>
