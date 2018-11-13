/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
<FullScreenViewport>
  <v-container>
    <v-dialog
      :value="userDialog"
      persistent
      max-width="500px">
      <GirderAuth
        :register="true" />
    </v-dialog>
  </v-container>
</FullScreenViewport>
</template>
<script>
import { Authentication as GirderAuth } from "@girder/components/src/components";

export default {
  name: "Login",
  components: {
    GirderAuth
  },
  inject: ["girderRest"],
  data() {
    return {
      form: "login",
      userDialog: true
    };
  },
  watch: {
    'girderRest.user'(user) {
      if (user) {
        this.$router.push("/explore");
      }
    }
  }
};
</script>
