import Vue from 'vue'
import Router from 'vue-router'
import Explore from './views/Explore.vue'
import Focus from './views/Focus.vue'

Vue.use(Router)

export default new Router({
  routes: [{
    path: '/',
    redirect: '/explore',
  },
  {
    path: '/explore',
    name: 'explore',
    component: Explore
  },
  {
    path: '/focus',
    name: 'focus',
    component: Focus
  }]
})
