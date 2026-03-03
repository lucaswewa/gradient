<template>
  <div>
    <ul>
      <li v-for="projector in projectors" :key="projector" class="uk-nav-header">{{ projector.label }}
        <propertyControl
          :thing-name="projector.name"
          property-name="led"
          label="LED on/off"
        />
        <propertyControl
          :thing-name="projector.name"
          property-name="colour"
          label="Color"
        />
        <propertyControl
          :thing-name="projector.name"
          property-name="blob_brightness"
          label="Brightness"
        />
      </li>
    </ul>
  </div>
</template>

<script>
import propertyControl from '@/components/labThingsComponents/propertyControl.vue';

export default {
  name: "projectorControl",

  components: {
    propertyControl,
  },

  data: function() {
    return {
      projectors: [
        {name: "projector_r", label: "Projector Red"},
        {name: "projector_g", label: "Projector Grn"},
        {name: "projector_b", label: "Projector Blu"},
      ]
    }
  }
}
</script>

<style lang="less" scoped>
</style>

