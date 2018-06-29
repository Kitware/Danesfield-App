import Vue from 'vue'
import ResonantGeo from 'resonantgeo/src';
import { Session } from 'resonantgeo/src/rest';
import { API_URL } from './constants';
import eventstream from './utils/eventstream';

import App from './App.vue';
import router from './router';
import store from './store';
import girder from './girder';

Vue.config.productionTip = false;

eventstream.open();
girder.girder = new Session({ apiRoot: API_URL });
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
