import Vue from 'vue';
import ResonantGeo from 'resonantgeo';
import { Session } from 'resonantgeo/src/rest';
import '@fortawesome/fontawesome-free/css/all.css';

import { API_URL } from './constants';
import App from './App.vue';
import router from './router';
import store from './store';
import girder from './girder';
import VuePortals from './vue-portals';

Vue.config.productionTip = process.env.NODE_ENV !== 'production';

girder.girder = new Session({ apiRoot: API_URL, enableSSE: true });
girder.girder.$refresh().then(() => {
  Vue.use(ResonantGeo, {
    girder: girder.girder,
  });
  Vue.use(VuePortals);
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app');
});
