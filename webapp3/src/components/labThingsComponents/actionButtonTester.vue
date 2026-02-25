<template>
  <div class="host-input">
    <div v-if="true">
      <div>
        <div class="uk-margin-small-bottom">
          <b>ActionButton no modal</b>
          <br />
        </div>
        <action-button
          v-if="true"
          thing="stage"
          action="move_relative"
          submit-label="move relative"
          :can-terminate="true"
          :poll-interval="0.05"
          :submit-data="{ block_cancellation: false, x: -500 }"
        />
      </div>
      <div>
        <div class="uk-margin-small-bottom">
          <b>ActionButton modal</b>
          <br />
        </div>
        <action-button
          v-if="true"
          thing="stage"
          action="move_relative"
          submit-label="move relative"
          :can-terminate="true"
          :poll-interval="0.05"
          :requires-confirmation="true"
          :button-primary="true"
          :modal-progress="true"
          :stream-with-modal="true"
          :submit-data="{ block_cancellation: false, x: 500 }"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ActionButton from "./actionButton.vue";
import useLTI from "@/mixins/labThingsMixins";
const lti = useLTI();

export default {
  name: "ActionButtonTester",
  components: {
    ActionButton,
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
    lti.thingDescriptions("http://localhost:5000/thing_descriptions")
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
.input-and-buttons-container {
  display: flex;
  flex-flow: column wrap;
  justify-content: flex-start;
  align-content: stretch;
  align-items: center;
  width: 100%;
}
.numeric-setting-line-input {
  flex-grow: 1;
  margin: 5px 0px;
  width: 5em;
  /* Stop Firefox showing input spinners, other
  browsers set with block below */
  -moz-appearance: textfield;
}
/* Chrome, Safari, Edge, Opera */
.numeric-setting-line-input::-webkit-outer-spin-button,
.numeric-setting-line-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
}
</style>
