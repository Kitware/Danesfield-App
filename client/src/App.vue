<template>
<v-app>
    <AppToolbar 
    :tabs='tabs' 
    :title='title' 
    :userIcon='userIcon' 
    @click-user='loginDialog = true' />
    
    <router-view />
</v-app>
</template>

<style>
html,
body,
.application,
.application--wrap {
  height: 100vh;
  overflow: hidden;
}

/* overwrite */
.btn--block {
  min-width: 0;
}
</style>

<script>
export default {
  name: "App",
  components: {
  },
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
