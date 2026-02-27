<template>
  <!-- Grid managing tab content -->
  <div class="uk-height-1-1 uk-grid-divider uk-margin-remove uk-padding-remove" uk-grid>
    <!-- grid column 1: Grid managing tab content -->
    <div uk-grid class="uk-height-1-1 uk-margin-remove uk-padding-remove">
      <!-- <calibrationWizard ref="calibrationWizard"></calibrationWizard> -->
      <div class="settings-nav">
        <ul class="uk-nav uk-nav-default">
          <li class="uk-nav-header">Application Settings</li>
          <li v-for="item in appTabs" :key="'setting-' + item.id + '-tab-content'">
            <tabIcon
              :id="'setting-' + item.id + '-tab-content'"
              :tab-i-d="item.id"
              :show-title="false"
              :show-tooltip="false"
              :require-connection="item.requireConnection"
              :current-tab="currentTab"
              @set-tab="setTab"
            >
              {{ item.title }}
            </tabIcon>
          </li>
          <li class="uk-nav-header">Microscope Settings</li>
          <button
            submit-label="Launch Calibration Wizard"
            type="button"
            class="uk-button uk-button-default uk-width-1-1"
            @click="startModals"
          >
            Launch Calibration Wizard
          </button>
          <li v-for="item in calibrationTabs" :key="'setting-' + item.id + '-tab-icon'">
            <tabIcon
              :id="'setting-' + item.id + '-tab-icon'"
              :tab-i-d="item.id"
              :show-title="false"
              :show-tooltip="false"
              :require-connection="item.requireConnection"
              :current-tab="currentTab"
              @set-tab="setTab"
            >
              {{ item.title }}
            </tabIcon>
          </li>
        </ul>
      </div>
      <div class="view-component uk-width-expand uk-padding-small">
        <tabContent
          v-for="item in allTabs"
          :id="'setting-' + item.id + '-tab-content'"
          :key="'setting-' + item.id + '-tab-content'"
          :tab-i-d="item.id"
          :require-connection="item.requireConnection"
          :current-tab="currentTab"
        >
          <component :is="item.component"></component>
        </tabContent>
      </div>
    </div>
    <!-- grid column 2: miniStreamDisplay -->
    <div id="mini-stream" class="uk-width-expand uk-padding-medium">
      <miniStreamDisplay />
    </div>
  </div>
</template>

<script>
import myDisplaySettings from "./settingsComponents/myDisplaySettings.vue";
import myCameraSettings from "./settingsComponents/myCameraSettings.vue";
import myStageSettings from "./settingsComponents/myStageSettings.vue";
import miniStreamDisplay from "../genericComponents/miniStreamDisplay.vue";

// Import generic components
import tabIcon from "../genericComponents/tabIcon.vue";
import tabContent from "../genericComponents/tabContent.vue";
import { markRaw } from "vue";

import { useStore } from "@/store";
import useLTI from "@/mixins/labThingsMixins";

const lti = useLTI();

// Export main app
export default {
  name: "MySettingsContent",

  components: {
    tabIcon,
    tabContent,
    myCameraSettings,
    myDisplaySettings,
    myStageSettings,
    miniStreamDisplay,
  },

  data: function () {
    return {
      selected: "display",
      currentTab: "display",
      coreAppTabs: [
        {
          id: "display",
          title: "Display",
          requireConnection: false,
          component: markRaw(myDisplaySettings),
          requiredThings: [],
        },
      ],
      coreCalibrationTabs: [
        {
          id: "camera",
          title: "Camera",
          requireConnection: true,
          component: markRaw(myCameraSettings),
          requiredThings: [],
        },
        {
          id: "stage",
          title: "Stage",
          requireConnection: true,
          component: markRaw(myStageSettings),
          requiredThings: ["stage"],
        },
        // {
        //   id: "mapping",
        //   title: "Camera to Stage Mapping",
        //   requireConnection: true,
        //   component: markRaw(CSMSettings),
        //   requiredThings: ["camera_stage_mapping"],
        // },
      ],
      store: () => useStore(),
    };
  },

  computed: {
    allTabs() {
      return [...this.appTabs, ...this.calibrationTabs];
    },
    appTabs() {
      // Filter core top tabs based on available Things.
      return this.coreAppTabs.filter((tab) => {
        if (!tab.requiredThings || tab.requiredThings.length === 0) return true;
        return tab.requiredThings.every((thing) => lti.thingAvailable(thing));
      });
    },
    calibrationTabs() {
      // Filter core top tabs based on available Things.
      return this.coreCalibrationTabs.filter((tab) => {
        if (!tab.requiredThings || tab.requiredThings.length === 0) return true;
        return tab.requiredThings.every((thing) => lti.thingAvailable(thing));
      });
    },
  },
  methods: {
    setTab: function (event, tab) {
      if (!(this.currentTab == tab)) {
        this.currentTab = tab;
      }
    },
    startModals: function () {
      // this.$refs.calibrationWizard.force_show();
    },
  },
};
</script>

<style lang="less" scoped>
// Custom UIkit CSS modifications
@import "../../assets/less/theme.less";

.settings-nav {
  overflow-y: auto;
  overflow-x: hidden;
  width: 200px;
  padding: 10px;
  background-color: rgba(180, 180, 180, 0.03);
  border-width: 0 1px 0 0;
  border-style: solid;
  border-color: rgba(180, 180, 180, 0.25);
}

.settings-nav li > a {
  padding-left: 6px !important;
  border-radius: @button-border-radius;
}

#mini-stream {
  min-width: 640px;
  max-width: 1440px;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  margin-top: 10px;
}
</style>
