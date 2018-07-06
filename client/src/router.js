import Vue from 'vue';
import Router from 'vue-router';
import Explore from './views/Explore.vue';
import Focus from './views/Focus.vue';
import Login from './views/Login.vue';
import ObjPage from './views/ObjPage.vue';

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
    path: '/objviewer',
    name: 'objviewer',
    component: ObjPage
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  }]
})
