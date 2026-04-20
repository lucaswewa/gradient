// import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import store from './store'
import UIkit from 'uikit'

import 'material-symbols/outlined.css'

// UIKit overrides
UIkit.mixin(
  {
    data: {
      animation: false,
    },
  },
  "accordion",
);

const app = createApp(App)

app.use(createPinia())

app.mount('#app')
