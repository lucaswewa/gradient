<template>
  <div id="stageSettings" ref="stageSettingsContainer" class="uk-width-medium">
    The microscope stage is a <b>{{ stageType }}</b>
    <div>
      <div class="uk-margin">
        <p>Your z motor iz currently {{ z_inverted }} inverted.</p>
        <p>We expect that moving in +z:</p>
        <ul>
          <li>Moves your objective up, towards the sample and illumination.</li>
          <li>Turns the exposed z gear counter-clockwise (when viewed from above>)</li>
        </ul>
        <p>If this is not the case, click the button below to switch.</p>
        <div>
          <action-button
            class="uk-width-1-2"
            thing="stage"
            action="invert-axis-direction"
            :submit-data="{axis: 'z'}"
            submit-label="Invert z"
            @response="readAxis()"
          />
        </div>
      </div>
    </div>


    <p><b>Single Move Step Size</b></p>
    <p>
      This sets the size (and direction) of movements made using the navigation buttons in the
      control tab or using the keyboard (arrow keys, page up/down).
    </p>
    <p>These settings do not affect the operation of other actions your microscope performs.</p>
    <div class="uk-grid-small uk-child-width-1-3" uk-grid>
      <div>
        <label class="uk-form-label" for="form-stacked-text">x</label>
        <div class="uk-form-controls">
          <input v-model="stepSize.x" class="uk-input uk-form-small" type="number" />
        </div>
        <label class="uk-margin-small-right">
          <input v-model="invert.x" class="uk-checkbox" type="checkbox" />
          Invert x
        </label>
      </div>

      <div>
        <label class="uk-form-label" for="form-stacked-text">y</label>
        <div class="uk-form-controls">
          <input v-model="stepSize.y" class="uk-input uk-form-small" type="number" />
        </div>
        <label class="uk-margin-small-right">
          <input v-model="invert.y" class="uk-checkbox" type="checkbox" />
          Invert y
        </label>
      </div>

      <div>
        <label class="uk-form-label" for="form-stacked-text">z</label>
        <div class="uk-form-controls">
          <input v-model="stepSize.z" class="uk-input uk-form-small" type="number" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ActionButton from "../../labThingsComponents/actionButton.vue";
import { useIntersectionObserver } from "@vueuse/core";

import { useStore } from "@/store";
import useLTI from "@/mixins/labThingsMixins";
const lti = useLTI();

export default {
  name: "myStageSettings",

  components: {
    ActionButton,
  },

  data: function () {
    return {
      z_inverted: "",
      store: () => useStore(),
    };
  },

  computed: {
    stageType: function () {
      return lti.thingDescription("stage").title;
    },
    stageMeasureAvailable() {
      return lti.thingAvailable("stage_measure");
    },
    // Note that as stepSize and invert are mutated (i.e. we change stepSize.x not stepSize)
    // rather than directly set we cannot use get() and set() computed to interact with the
    // store as changed won't be detected by set(). Instead use a deep watcher to
    // update the store (see ``watch:`` below)
    stepSize() {
      return this.store().state.navigationStepSize;
    },
    invert() {
      return this.store().state.navigationInvert;
    },
  },


  watch: {
    stepSize: {
      deep: true,
      handler(newVal) {
        this.store().changeNavigationStepSize(newVal);
      },
    },
    invert: {
      deep: true,
      handler(newVal) {
        this.store().changeNavigationInvert(newVal);
      },
    },
  },

  mounted() {
    useIntersectionObserver(
      this.$refs.stageSettingsContainer,
      ([{ isIntersecting }]) => {
        this.visibilityChanged(isIntersecting);
      },
      { threshold: 0.0 },
    );
  },

  methods: {
    visibilityChanged(isVisible) {
      if (isVisible) {
        this.readAxis();
      }
    },
    async readAxis() {
      let axes_inverted = await lti.readThingProperty("stage", "axis_inverted");
      this.z_inverted = axes_inverted["z"] ? "" : "not ";
    },
  },
};
</script>

<style lang="less" scoped>
#mini-stream {
  min-width: 400px;
  // max-width: 600px;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  margin-top: 50px;
}
</style>
