<template>
<v-app>
    <AppToolbar
    :title="title"
    :tabs="tabs"
    :panelButton="true"
    @click-panel="$store.commit('toggleSidePanel')">
      <template slot="right">
        <GirderUserButton 
          @login="userForm='login';userDialog=true;"
          @user="userForm='logout';userDialog=true;" />
      </template>
    </AppToolbar>

    <transition name="fade" mode="out-in">
      <router-view></router-view>
    </transition>
    <GirderUserDialog
      :form.sync='userForm'
      v-model='userDialog'
      />
    <Prompt />
</v-app>
</template>

<script>
import eventstream from "./utils/eventstream";
import Prompt from "./components/prompt/Prompt";
import { mapActions } from "vuex";

import "./transitions.scss";

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
        },
        {
          title: "Jobs",
          route: "/job",
          icon: "fa-tasks"
        }
      ],
      userForm: "login",
      userDialog: false
    };
  },
  created() {
    function displayJobStatus(statusCode) {
      switch (statusCode) {
        case 0:
          return "inactive";
        case 1:
          return "queued";
        case 2:
          return "running";
        case 3:
          return "suceeded";
      }
    }
    eventstream.on("job_created", e => {
      this.prompt({
        message: `${e.data.title} is ${displayJobStatus(e.data.status)}`
      });
    });
    eventstream.on("job_status", e => {
      this.prompt({
        message: `${e.data.title} is ${displayJobStatus(e.data.status)}`
      });
    });
  },
  methods: {
    ...mapActions("prompt", ["prompt"])
  }
};
</script>

<style>
/* global */
html,
body,
.application,
.application--wrap {
  height: 100vh;
  overflow: hidden;
}

/* overwrite */
.v-btn {
  min-width: 0;
}
</style>
