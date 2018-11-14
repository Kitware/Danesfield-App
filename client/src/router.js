/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

import Vue from 'vue';
import Router from 'vue-router';
import Explore from './views/Explore.vue';
import Focus from './views/Focus.vue';
import Job from './views/Job.vue';
import Login from './views/Login.vue';

Vue.use(Router);
import girder from './girder';

function beforeEnter(to, from, next) {
  if (!girder.girder.user) {
    next('/login');
  } else {
    next();
  }
}

export default new Router({
  routes: [{
    path: '/',
    redirect: '/explore',
  },
  {
    path: '/explore',
    name: 'explore',
    component: Explore,
    beforeEnter
  },
  {
    path: '/focus',
    name: 'focus',
    component: Focus,
    beforeEnter
  },
  {
    path: '/job',
    name: 'job',
    component: Job,
    beforeEnter
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  }]
})
