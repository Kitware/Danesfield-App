/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import Vue from 'vue';
import ResonantGeo from 'resonantgeo';
import { Session } from 'resonantgeo/src/rest';
import '@fortawesome/fontawesome-free/css/all.css';
import VueCesium from 'vue-cesium';

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
  Vue.use(VueCesium, {
    // default Cesium Ion API key
    accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1MDA2NzVhYi05NjljLTQ2ZWQtYWJkZC1jYTg4NzA4YjEzNGMiLCJpZCI6MjU5LCJpYXQiOjE2MjUxNTA1ODh9.hDxkoBgpk13oYPDuKYhkt6XSyii_kUKufDE_GLE38is'
  });
  Vue.use(VuePortals);
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app');
});
