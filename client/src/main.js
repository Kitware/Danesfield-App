import Vue from 'vue'
import ResonantGeo from 'resonantgeo';
import { Session } from 'resonantgeo/src/rest';
import '@fortawesome/fontawesome-free/css/all.css';

import { API_URL } from './constants';
import App from './App.vue';
import router from './router';
import store from './store';
import girder from './girder';

Vue.config.productionTip = false;

girder.girder = new Session({ apiRoot: API_URL, enableSSE: true });
girder.girder.$refresh().then(() => {
  Vue.use(ResonantGeo, {
    girder: girder.girder,
  });
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app');
});
