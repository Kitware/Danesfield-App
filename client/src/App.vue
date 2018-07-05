<template>
<v-app>
    <AppToolbar
    :title="title"
    :tabs='tabs'>
      <template slot="right">
        <GirderUserButton 
          @login="userForm='login';userDialog=true;"
          @user="userForm='logout';userDialog=true;" />
      </template>
    </AppToolbar>

    <transition name="fade" mode='out-in'>
      <router-view></router-view>
    </transition>
    <GirderUserDialog
      :form.sync='userForm'
      v-model='userDialog'
      />
    <Prompt />
</v-app>
</template>

<style>
/* global */
html,
body,
.application,
.application--wrap {
  height: 100vh;
  overflow: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.15s ease;
}
.slide-fade-leave-active {
  transition: all 0.15s ease;
}
.slide-fade-enter {
  transform: translateX(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(10px);
  opacity: 0;
}

/* overwrite */
.btn {
  min-width: 0;
}
</style>

<script>
import Prompt from "./components/prompt/Prompt";

export default {
  name: "App",
  components: { Prompt },
  data() {
    return {
      title: "Core3D",
      tabs: [
        {
          title: "Explore",
          route: "/explore",
          icon: "explore"
        },
        {
          title: "Focus",
          route: "/focus",
          icon: "center_focus_strong"
        }
      ],
      userForm: "login",
      userDialog: false
    };
  },
  methods: {
  }
};
</script>
