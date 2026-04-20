<template>
  <div id="app-content" class="uk-margin-remove uk-padding-remove uk-height-1-1" uk-grid>
    <!-- Initialisation modals -->
    <calibrationWizard ref="calibrationWizard" @on-close="enterApp()"></calibrationWizard>
    <!-- Vertical tab bar -->
    <div id="switcher-left-container">
      <div
        id="switcher-left"
        class="uk-flex uk-flex-column uk-padding-remove uk-width-auto uk-height-1-1 uk-text-center"
      >
        <!-- For each top tab -->
        <template v-for="(item, index) in topTabs" :key="item.id + '-tab-icon'">
          <!-- Render the tab icon -->
          <tabIcon
            :id="item.id + '-tab-icon'"
            :tab-i-d="item.id"
            :title="item.title"
            :require-connection="true"
            :current-tab="currentTab"
            :class="item.class"
            @set-tab="setTab"
          >
            <img
              v-if="item.iconURL"
              style="filter: grayscale(100%); width: 22px; margin-top: 5px; margin-bottom: 8px"
              :src="item.iconURL"
            />
            <span v-if="!item.iconURL" class="material-symbols-outlined">
              {{ item.icon }}
            </span>
          </tabIcon>
          <!-- Add a divider if item.divide is true -->
          <hr v-if="item.divide" :key="'tab-divider-' + index" />
        </template>

        <hr id="extension-tab-divider" />

        <!-- For each bottom tab -->
        <template v-for="(item, index) in bottomTabs" :key="item.id + '-tab-icon'">
          <!-- Render the tab icon -->
          <tabIcon
            :id="item.id + '-tab-icon'"
            :tab-i-d="item.id"
            :title="item.title"
            :require-connection="true"
            :current-tab="currentTab"
            :class="item.class"
            @set-tab="setTab"
          >
            <span class="material-symbols-outlined">{{ item.icon }}</span>
          </tabIcon>
          <!-- Add a divider if item.divide is true -->
          <hr v-if="item.divide" :key="'tab-divider-' + index" />
        </template>
      </div>
    </div>

    <!-- Corresponding vertical tab content -->
    <div
      id="container-left"
      ref="containerLeft"
      class="uk-padding-remove uk-height-1-1 uk-width-expand"
    >
      <tabContent
        v-for="item in allTabs"
        :id="item.id + '-tab-content'"
        :key="item.id + '-tab-content'"
        :tab-i-d="item.id"
        :require-connection="true"
        :current-tab="currentTab"
      >
        <component :is="item.component" @scroll-top="scrollToTop"></component>
      </tabContent>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, useTemplateRef, computed, onMounted, markRaw } from "vue";
import store from "@/store";
import { eventBus } from "@/eventBus";

// Import generic components
import tabIcon from "./genericComponents/tabIcon.vue";
import tabContent from "./genericComponents/tabContent.vue";

// Import new content components
import aboutContent from "./tabContentComponents/aboutContent.vue";
import controlContent from "./tabContentComponents/controlContent.vue";
import loggingContent from "./tabContentComponents/loggingContent.vue";
import powerContent from "./tabContentComponents/powerContent.vue";
import scanListContent from "./tabContentComponents/scanListContent.vue";
import settingsContent from "./tabContentComponents/settingsContent.vue";
import slideScanContent from "./tabContentComponents/slideScanContent.vue";
import viewContent from "./tabContentComponents/viewContent.vue";

// Import modal components
import calibrationWizard from "./modalComponents/calibrationWizard.vue";

// --- Template Refs ---
const calibrationWizardRef = useTemplateRef("calibrationWizard");
const containerLeftRef = useTemplateRef("containerLeft");

// --- State ---
const currentTab = ref("view");

const bottomTabs = ref([
  {
    id: "settings",
    title: "Settings",
    icon: "settings",
    component: markRaw(settingsContent),
    class: "uk-margin-auto-top"
  },
  { id: "logging", title: "Logging", icon: "assignment_late", component: markRaw(loggingContent) },
  {
    id: "about",
    title: "About",
    icon: "info",
    component: markRaw(aboutContent)
  },
  {
    id: "power",
    title: "Power",
    icon: "power_settings_new",
    component: markRaw(powerContent)
  },
]);

const coreTopTabs = ref([
  {
    id: "view",
    title: "View",
    icon: "visibility",
    component: markRaw(viewContent),
    requiredThings: []
  },
  {
    id: "control",
    title: "Control",
    icon: "gamepad",
    component: markRaw(controlContent),
    requiredThings: []
  },
  {
    id: "slide-scan",
    title: "Slide Scan",
    icon: "settings_overscan",
    component: markRaw(slideScanContent),
    requiredThings: ["smart_scan"]
  },
  {
    id: "scan-list",
    title: "Scan List",
    icon: "photo_library",
    component: markRaw(scanListContent),
    requiredThings: ["smart_scan"]
  },
]);

// --- Computed ---
const topTabs = computed(() => {
  return coreTopTabs.value.filter((tab) => {
    if (!tab.requiredThings || tab.requiredThings.length === 0) return true;
    // Assuming thingAvailable is a store getter or helper. Adjust according to your project.
    return tab.requiredThings.every((thing) => store.getters['wot/thingAvailable'](thing));
  });
});

const allTabs = computed(() => [...topTabs.value, ...bottomTabs.value]);

const tabOrder = computed(() => {
  return allTabs.value.map(tab => tab.id);
});

const currentTabIndex = computed(() => {
  return tabOrder.value.indexOf(currentTab.value);
});

// --- Methods ---
const setTab = (event, tab) => {
  if (currentTab.value !== tab) {
    currentTab.value = tab;
  }
};

const incrementTabBy = (n) => {
  const len = tabOrder.value.length;
  const newIndex = (((currentTabIndex.value + n) % len) + len) % len;
  currentTab.value = tabOrder.value[newIndex];
};

const startModals = () => {
  calibrationWizardRef.value?.show_if_needed();
};

const enterApp = () => {
  // Logic for after initialization
};

const scrollToTop = () => {
  containerLeftRef.value?.scrollTo({ top: 0 });
};

// --- Lifecycle ---
onMounted(() => {
  eventBus.on("globalSwitchTab", (tabID) => {
    currentTab.value = tabID;
  });

  eventBus.on("globalIncrementTab", () => {
    incrementTabBy(1);
  });

  eventBus.on("globalDecrementTab", () => {
    incrementTabBy(-1);
  });

  if (store.getters.ready) {
    startModals();
  }
});
</script>

<style scoped lang="less">
.window-container {
  width: 100%;
  height: 100%;
}
#component-left {
  width: 100%;
  height: 100%;
}

#container-left {
  overflow: auto;
  background-color: rgba(180, 180, 180, 0.025);
  width: 100%;
  height: 100%;
}

#switcher-left {
  width: 85px;
  padding-top: 2px !important;
}

#switcher-left-container {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  overflow-y: auto;
  height: 100%;
  background-color: rgba(180, 180, 180, 0.1);
  border-width: 0 1px 0 0;
  border-style: solid;
  border-color: rgba(180, 180, 180, 0.25);
}

#switcher-left a {
  padding: 10px 8px;
}
</style>
