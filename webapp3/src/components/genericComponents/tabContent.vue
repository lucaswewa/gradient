<template>
  <div
    v-if="!(requireConnection && !store().ready)"
    :hidden="currentTab != tabID"
    class="uk-width-expand uk-height-1-1"
  >
    <slot></slot>
  </div>
</template>

<script>
import { useStore } from "../../store.js";

export default {
  name: "TabContent",

  props: {
    tabID: {
      type: String,
      required: true,
    },
    currentTab: {
      type: String,
      required: true,
    },
    requireConnection: Boolean,
  },

  data: function () {
    return {
      store: () => useStore(),
    };
  },

  computed: {},

  methods: {},
};
</script>

<style lang="less" scoped>
.section-heading {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  line-height: 20px;
  cursor: default;
}
</style>
