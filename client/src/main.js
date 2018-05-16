import Vue from 'vue'
import Vuetify from 'vuetify'
import ResonantGeo from 'resonantgeo/src';
import { setApiUrl, getTokenFromCookie } from 'girder/src/rest';
import { API_URL } from './constants';

import App from './App.vue';
import router from './router';
import store from './store';


Vue.config.productionTip = false;
Vue.use(Vuetify);
Vue.use(ResonantGeo);

setApiUrl(API_URL);
store.commit('auth/setToken', getTokenFromCookie());
store.dispatch('auth/whoami').then(() => new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app'));
