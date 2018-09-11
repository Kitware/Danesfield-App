<template>
<v-app>
    <AppToolbar
    title="title"
    :panelButton="true"
    class="app-toolbar"
    @click-panel="$store.commit('toggleSidePanel')">
      <template slot="left">
        <v-tabs
          icons-and-text
          :height='64'
          color='transparent'>
            <v-tab
              to="/explore">
              Explore
              <v-icon>explore</v-icon>
            </v-tab>
            <v-tab
              to="/focus">
              Focus
              <v-icon>center_focus_strong</v-icon>
            </v-tab>
            <v-tab
              to="/job">
              Jobs
              <v-badge :value="runningJobIds.length">
                <v-icon
                  slot="badge"
                  dark
                  class="mb-0 rotate">autorenew</v-icon>
                <v-icon>fa-tasks</v-icon>
              </v-badge>
            </v-tab>
            <v-tab
              :href="GIRDER_URL"
              target="_blank">
              Girder
              <v-icon>open_in_new</v-icon>
            </v-tab>
        </v-tabs>
      </template>
      <template slot="title">
        <v-toolbar-title>
          <Portal name="title" />
        </v-toolbar-title>
      </template>
      <template slot="right">
        <GirderUserButton 
          @login="userForm='login';userDialog=true;"
          @user="userForm='logout';userDialog=true;" />
      </template>
    </AppToolbar>
    <FullScreenViewport>
      <transition name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
    </FullScreenViewport>
    <GirderUserDialog
      :form.sync='userForm'
      v-model='userDialog'
      />
    <Prompt />
</v-app>
</template>

<script>
import { mapActions } from "vuex";

import girder from "./girder";
import Prompt from "resonantgeoview/src/components/prompt/Prompt";
import { status } from "resonantgeo/src/components/girder/jobs";
import { GIRDER_URL } from "./constants";

import "./transitions.scss";

let jobStatus = status.all();

export default {
  name: "App",
  components: { Prompt },
  data() {
    return {
      portal: {
        name: "title",
        text: "Core3D"
      },
      GIRDER_URL,
      userForm: "login",
      userDialog: false,
      runningJobIds: []
    };
  },
  async created() {
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

    let { data: runningJobs } = await girder.girder.get("/job", {
      params: {
        statuses: `[${jobStatus.RUNNING.value}]`
      }
    });
    this.runningJobIds = runningJobs.map(job => job._id);

    girder.girder.sse.$on("message:job_status", ({ data: job }) => {
      let jobId = job._id;
      switch (job.status) {
        case jobStatus.RUNNING.value:
          if (this.runningJobIds.indexOf(jobId) === -1) {
            this.runningJobIds.push(jobId);
          }
          break;
        case jobStatus.SUCCESS.value:
        case jobStatus.ERROR.value:
          if (this.runningJobIds.indexOf(jobId) !== -1) {
            this.runningJobIds.splice(this.runningJobIds.indexOf(jobId), 1);
          }
          break;
      }
    });
  },
  methods: {
    ...mapActions("prompt", ["prompt"])
  }
};
</script>

<style lang="scss">
/* global */
html,
body,
.application,
.application--wrap {
  height: 100vh;
  overflow: hidden;
}

.flex1 {
  flex: 1 1 auto;
}

.rotate {
  animation: rotation 1.5s infinite linear;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

/* overwrite */
.v-btn {
  min-width: 0;
}

/* local */
.v-toolbar.app-toolbar {
  .v-tabs {
    width: initial;

    .v-tabs__div {
      min-width: 100px;
    }

    .v-badge {
      .v-badge__badge {
        top: -7px;
        right: -24px;
      }
    }
  }

  // This is a wierd fix needed for the login label
  button .v-btn__content {
    height: inherit;
  }
}
</style>
