<template>
  <div class="host-input">
    <div v-if="store().state.available">
      <div>
        <div class="uk-margin-small-bottom">
          <b>Thing:</b> TesterThing
        </div>
        <div class="uk-margin-small-bottom">
          Action: flash
        </div>
        <action-button
          thing="tester"
          action="flash"
          submit-label="Flash"
          :can-terminate="false"
          :submit-data="{ dt: 2 }"
        />
      </div>
      <hr />
      <div class="uk-flex uk-flex-center uk-flex-middle uk-margin">
        <div
          class="dpad-grid"
          :class="{
            'dpad-only': false,
            'focus-only': false,
            'both-controls': true,
          }"
        >
          <label id="jog-label" class="uk-text-small uk-text-center dpad-btn">Jog Controls</label>
          <label id="focus-label" class="uk-text-small uk-text-center dpad-btn">Focus Controls</label>

          <button
            id="up-button"
            class="uk-button uk-button-primary dpad-btn"
            @pointerdown="jog($event, 0, 1, 0)"
            @pointerup="jogStop()"
            @mouseLeave="jogStop()"
          >
            <span class="material-symbols-outlined sync-icon"> arrow_upward </span>
          </button>

          <button
            id="left-button"
            class="uk-button uk-button-primary dpad-btn"
            @pointerdown="jog($event, -1, 0, 0)"
            @pointerup="jogStop()"
            @pointercancel="jogStop()"
          >
            <span class="material-symbols-outlined sync-icon"> arrow_back </span>
          </button>

          <button
            id="right-button"
            class="uk-button uk-button-primary dpad-btn"
            @pointerdown="jog($event, 1, 0, 0)"
            @pointerup="jogStop()"
            @pointercancel="jogStop()"
          >
            <span class="material-symbols-outlined sync-icon"> arrow_forward </span>
          </button>

          <button
            id="down-button"
            class="uk-button uk-button-primary dpad-btn"
            @pointerdown="jog($event, 0, -1, 0)"
            @pointerup="jogStop()"
            @pointercancel="jogStop()"
          >
            <span class="material-symbols-outlined sync-icon"> arrow_downward </span>
          </button>

          <button
            id="focus-out-button"
            class="uk-button uk-button-primary dpad-btn"
            @pointerdown="jog($event, 0, 0, -1)"
            @pointerup="jogStop()"
            @pointercancel="jogStop()"
          >
            <span class="material-symbols-outlined sync-icon"> remove </span>
          </button>

          <button
            id="focus-in-button"
            class="uk-button uk-button-primary dpad-btn"
            @pointerdown="jog($event, 0, 0, 1)"
            @pointerup="jogStop()"
            @pointercancel="jogStop()"
          >
            <span class="material-symbols-outlined sync-icon"> add </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ActionButton from "../../labThingsComponents/actionButton.vue";
import { useStore } from "../../../store.js";
import useLTI from "@/mixins/labThingsMixins";

const lti = useLTI();

export default {
  name: "ActionPane",
  components: {
    ActionButton,
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


<style scoped>
.dpad-grid {
  display: grid;
  grid-template-columns: repeat(5, 40px);
  gap: 1px;
  justify-content: center;
  align-items: center;
}

.both-controls {
  grid-template-rows: 40px 20px 40px 40px 40px;
}

.dpad-only {
  grid-template-rows: 40px 40px 40px;
}

.focus-only {
  grid-template-rows: 40px;
}

/* Place buttons within grid */
.both-controls #jog-label {
  grid-column: 2;
  grid-row: 1;
}
.both-controls #focus-label {
  grid-column: 5;
  grid-row: 1;
}

.dpad-grid #up-button {
  grid-column: 2;
  grid-row: 3;
}
.dpad-grid #left-button {
  grid-column: 1;
  grid-row: 4;
}
.dpad-grid #right-button {
  grid-column: 3;
  grid-row: 4;
}
.dpad-grid #down-button {
  grid-column: 2;
  grid-row: 5;
}

.both-controls #focus-out-button {
  grid-column: 5;
  grid-row: 5;
}
.both-controls #focus-in-button {
  grid-column: 5;
  grid-row: 3;
}

.focus-only #focus-out-button {
  grid-column: 1;
  grid-row: 1;
}
.focus-only #focus-in-button {
  grid-column: 3;
  grid-row: 1;
}

.dpad-btn {
  width: 40px;
  height: 40px;
  justify-content: center;
  align-items: center;
  display: flex;
}
</style>
