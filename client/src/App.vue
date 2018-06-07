<template>
<v-app>
    <AppToolbar 
    :tabs='tabs' 
    :title='title' 
    :userIcon='userIcon' 
    @click-user='loginDialog = true' />

    <transition name="fade" mode='out-in'>
      <router-view></router-view>
    </transition>
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
.btn--block {
  min-width: 0;
}
</style>

<script>
export default {
  name: "App",
  components: {},
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
      userIcon: "account_circle",
      loginDialog: false,
      login: {
        email: "",
        password: "",
        rules: [v => !!v || "Field is required"]
      }
    };
  },
  methods: {
    submitLogin() {
      if (this.$refs.login.validate()) {
        console.log(`logged in as ${this.login.email}`);
        this.loginDialog = false;
      }
    }
  }
};
</script>
