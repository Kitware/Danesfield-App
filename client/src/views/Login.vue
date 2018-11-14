/*#############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
#############################################################################*/

<template>
<FullScreenViewport>
  <v-container>
    <GirderUserDialog
      appName='Danesfield'
      :form.sync='form'
      :value='userDialog'
      />
  </v-container>
</FullScreenViewport>
</template>
<script>
export default {
  name: "Login",
  data() {
    return {
      form: "login",
      userDialog: true
    };
  },
  computed: {
    user() {
      return this.$girder.user;
    }
  },
  watch: {
    user(user) {
      if (user) {
        this.$router.push("/explore");
      }
    }
  }
};
</script>
