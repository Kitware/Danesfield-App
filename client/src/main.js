/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import Vue from 'vue';
import ResonantGeo from 'resonantgeo';
import { Session } from 'resonantgeo/src/rest';
import Girder, { RestClient } from '@girder/components/src';
import NotificationBus from '@girder/components/src/utils/notifications';
import '@fortawesome/fontawesome-free/css/all.css';

import { API_URL } from './constants';
import App from './App.vue';
import router from './router';
import store from './store';
import girder from './girder';
import VuePortals from './vue-portals';

girder.girder = new RestClient({ apiRoot: API_URL });
var notificationBus = new NotificationBus(girder.girder, { useEventSource: true });
notificationBus.connect();
// A hack when transitioning from resonantgeo to girder_web_component
girder.girder.sse = notificationBus;

Vue.config.productionTip = process.env.NODE_ENV !== 'production'

Vue.use(Girder);

girder.girder.fetchUser().then(() => {
  Vue.use(ResonantGeo, {
    girder: girder.girder,
  });
  Vue.use(VuePortals);
  new Vue({
    router,
    store,
    render: h => h(App),
    provide: { girderRest: girder.girder, notificationBus },
  }).$mount('#app');
});
