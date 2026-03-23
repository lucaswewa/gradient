<template>
  <!-- Grid managing tab content -->
  <div class="uk-height-1-1 uk-grid-divider uk-margin-remove uk-padding-remove" uk-grid>
    <!-- grid column 1: Grid managing tab content -->
    <div uk-grid class="uk-height-1-1 uk-margin-remove uk-padding-remove">
      <!-- <calibrationWizard ref="calibrationWizard"></calibrationWizard> -->
      <div class="settings-nav">
        <ul class="uk-nav uk-nav-default">
          <li class="uk-nav-header">Manual Control</li>
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
          <li class="uk-nav-header">Microscope Control</li>
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
import myStageControlContent from "./controlComponents/myStageControlContent.vue";
import myProjectorControlContent from "./controlComponents/myProjectorControlContent.vue";
import myCameraControlContent from "./controlComponents/myCameraControlContent.vue";
import myDeviceControlContent from "./controlComponents/myDeviceControlContent.vue";
import MiniStreamDisplay from "../genericComponents/miniStreamDisplay.vue";

import tabIcon from "../genericComponents/tabIcon.vue";
import tabContent from "../genericComponents/tabContent.vue";
import { markRaw } from "vue";

import { useStore } from "@/store";
import useLTI from "@/mixins/labThingsMixins";

const lti = useLTI();

export default {
  name: "MyControlContent",

  components: {
    tabIcon,
    tabContent,
    // paneControl,
    MiniStreamDisplay,
    stageControlContent: myStageControlContent,
    projectorControlContent: myProjectorControlContent,
    cameraControlContent: myCameraControlContent,
    deviceControlContent: myDeviceControlContent
  },

  data: function() {
    return {
      selected: "stage",
      currentTab: "stage",
      coreAppTabs: [
        {
          id: "stage",
          title: "Stage",
          requireConnection: false,
          component: markRaw(myStageControlContent),
          requiredThings: [],
        },
        {
          id: "projector",
          title: "Projector",
          requireConnection: false,
          component: markRaw(myProjectorControlContent),
          requiredThings: [],
        },
        {
          id: "camera",
          title: "Camera",
          requireConnection: false,
          component: markRaw(myCameraControlContent),
          requiredThings: [],
        },
      ],
      coreCalibrationTabs: [
        {
          id: "device",
          title: "Device",
          requireConnection: false,
          component: markRaw(myDeviceControlContent),
          requiredThings: [],
        },
      ],
      store: () => useStore(),
    };
  },

  computed: {
    allTabs() {
      return [...this.appTabs, ...this.calibrationTabs];
    },
    appTabs() {
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
    setTab: function(event, tab) {
      if (!(this.currentTab == tab)) {
        this.currentTab = tab;
      }
    },
    startModals: function() {

    }
  }
};
</script>

<style lang="less" scoped>
// Custom UIkit CSS modifications
@import "../../assets/less/theme.less";

.settings-nav {
  overflow-y: auto;
  overflow-x: hidden;
  width: 180px;
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
  max-width: 1280px;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  margin-top: 10px;
}
</style>
