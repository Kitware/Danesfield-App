import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Explore from './views/Explore.vue'
import Focus from './views/Focus.vue'
import About from './views/About.vue'

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
  },
  {
    path: '/about',
    name: 'about',
    component: About
  }]
})
