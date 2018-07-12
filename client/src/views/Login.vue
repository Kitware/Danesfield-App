<template>
<FullScreenViewport>
  <v-container>
    <GirderUserDialog
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
