import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import UIkit from "uikit";

// Import MD icons
import "material-symbols/outlined.css";

// UIKit overrides
UIkit.mixin(
  {
    data: {
      animation: false,
    },
  },
  "accordion",
);

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)

app.mount('#app')
